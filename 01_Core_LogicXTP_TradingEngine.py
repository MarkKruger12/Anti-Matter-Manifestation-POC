import numpy as np
from itertools import product
from typing import Tuple, List, Dict

class XTP_PricingKernel:
    """Core pricing logic using Belnap-Jain 4-valued logic for Null-State events."""
    def __init__(self):
        self.CERN_BENCHMARK_USD_PER_G: float = 62.5e12          # $62.5 Trillion / g
        self.NG_TO_G: float = 1e-9
        # Belnap-Jain weights: (T-membership, F-membership)
        self.logic_weights: Dict[Tuple[int, int], float] = {
            (1, 0): 1.00,    # Manifested / Stable Stationary Trail
            (0, 1): 0.05,    # Annihilated / Gamma hedge value only
            (1, 1): 1.15,    # Coherent Superposition ? premium
            (0, 0): 0.00     # Null / No event
        }
        self.optimal_voltage: float = 10.8

    def calculate_duty_cycle_value(
        self,
        nanograms: float,
        state_vector: Tuple[int, int],
        voltage: float
    ) -> float:
        """
        Compute USD value of one XTP-1 duty cycle.
        
        Args:
            nanograms: Manifested antimatter in ng
            state_vector: Belnap-Jain (T, F) membership
            voltage: Pulse voltage (9–12 V range)
        
        Returns:
            Spot value in USD
        """
        base_value = nanograms * self.NG_TO_G * self.CERN_BENCHMARK_USD_PER_G
        multiplier = self.logic_weights.get(state_vector, 0.85)  # default discount
        vec = 1.0 - abs(self.optimal_voltage - voltage) / self.optimal_voltage
        return base_value * multiplier * max(0.0, vec)  # guard against extreme V


class XTP_TradingEngine(XTP_PricingKernel):
    """Full trading & steering engine with I-Ching Markov navigation."""
    def __init__(self):
        super().__init__()
        self.num_states: int = 64
        self.hexagram_to_index: Dict[Tuple[int, ...], int] = {
            tuple(bits): i for i, bits in enumerate(product([0, 1], repeat=6))
        }
        self.transition_matrix: np.ndarray = np.ones((64, 64)) / 64.0  # uniform prior
        self.state_history: List[Tuple[int, float, float]] = []  # (hex_idx, realized_mult, voltage)

    def get_next_optimal_voltage(
        self,
        current_hex_bits: Tuple[int, ...]
    ) -> Tuple[float, float]:
        """
        Markov prediction ? next best 9–12 V pulse to maximize expected Belnap premium.
        
        Returns:
            (optimal_voltage, expected_multiplier)
        """
        if len(current_hex_bits) != 6:
            raise ValueError("Hexagram must be 6-bit tuple")
        
        curr_idx = self.hexagram_to_index[current_hex_bits]
        next_probs = self.transition_matrix[curr_idx]
        
        voltages = np.linspace(9.0, 12.0, 61)  # 0.05 V resolution
        expected_payoffs = np.zeros(len(voltages))
        
        for i, v in enumerate(voltages):
            # In production: replace dummy with real Null-Gate classifier output
            dummy_state = (1, 1) if np.random.rand() < 0.68 else (1, 0)  # ~68% superposition bias
            mult = self.logic_weights.get(dummy_state, 0.85)
            vec = 1.0 - abs(self.optimal_voltage - v) / self.optimal_voltage
            expected_payoffs[i] = np.sum(next_probs * mult * max(0.0, vec))
        
        best_idx = np.argmax(expected_payoffs)
        return voltages[best_idx], expected_payoffs[best_idx]

    def update_after_pulse(
        self,
        current_hex_bits: Tuple[int, ...],
        next_hex_bits: Tuple[int, ...],
        realized_ng: float,
        realized_voltage: float,
        realized_state: Tuple[int, int] = (1, 1)
    ) -> float:
        """Bayesian update of transition matrix from real event."""
        curr = self.hexagram_to_index[current_hex_bits]
        nxt = self.hexagram_to_index[next_hex_bits]
        
        realized_value = self.calculate_duty_cycle_value(realized_ng, realized_state, realized_voltage)
        base = realized_ng * self.NG_TO_G * self.CERN_BENCHMARK_USD_PER_G
        realized_mult = realized_value / base if base > 0 else 0.0
        
        self.transition_matrix[curr] *= 0.92          # light forgetting
        self.transition_matrix[curr, nxt] += 1.0
        self.transition_matrix[curr] /= self.transition_matrix[curr].sum() + 1e-12
        
        self.state_history.append((curr, realized_mult, realized_voltage))
        return realized_value