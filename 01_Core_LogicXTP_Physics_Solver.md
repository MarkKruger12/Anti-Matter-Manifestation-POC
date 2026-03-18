# XTP-1 Duty Cycle Simulation – 1,000 Pulses

```python
%matplotlib inline
import numpy as np
import matplotlib.pyplot as plt
from XTP_TradingEngine import XTP_TradingEngine   # adjust relative import if needed
from XTP_PhysicsSolver import XTP_PhysicsSolver

engine = XTP_TradingEngine()
solver = XTP_PhysicsSolver()

np.random.seed(42)
n_pulses = 1000
values, voltages, multipliers, phi_stabs = [], [], [], []

current_hex = tuple(np.random.randint(0, 2, 6))

for i in range(n_pulses):
    next_v, _ = engine.get_next_optimal_voltage(current_hex)
    realized_ng = np.random.uniform(0.1, 1.5)
    realized_state = (1,1) if np.random.rand() < 0.72 else (1,0)
    
    value = engine.update_after_pulse(
        current_hex,
        tuple(np.random.randint(0, 2, 6)),  # simulate next hex
        realized_ng,
        next_v,
        realized_state
    )
    
    # Physics check
    V_mkt_sim = value / 1e6   # crude proxy: $M scale ? market potential
    phi, status = solver.numerical_stability_threshold(V_mkt_sim)
    
    values.append(value)
    voltages.append(next_v)
    multipliers.append(value / (realized_ng * 1e-9 * engine.CERN_BENCHMARK_USD_PER_G))
    phi_stabs.append(phi)
    
    # Cycle hexagram (toy model)
    current_hex = tuple((np.array(current_hex) + np.random.randint(-1,2,6)) % 2)

# ?? Dashboard ??
fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

axs[0].plot(values, label='Duty Value (USD)', color='C0')
axs[0].set_yscale('log')
axs[0].set_ylabel('Value $'); axs[0].legend(); axs[0].grid(alpha=0.3)

axs[1].plot(voltages, label='Pulse Voltage (V)', color='C1')
axs[1].axhline(10.8, color='k', ls='--', alpha=0.5, label='Optimal')
axs[1].set_ylabel('Voltage'); axs[1].legend(); axs[1].grid(alpha=0.3)

axs[2].plot(phi_stabs, label='Trail Amplitude |?|', color='C2')
axs[2].axhline(0.8, color='g', ls='--', alpha=0.5, label='Stable threshold')
axs[2].axhline(0.3, color='r', ls='--', alpha=0.5, label='Evaporation risk')
axs[2].set_ylabel('Stability'); axs[2].legend(); axs[2].grid(alpha=0.3)

plt.xlabel('Pulse #'); plt.suptitle('XTP-1 1,000 Duty Cycle Simulation', fontsize=16)
plt.tight_layout()
plt.show()

print(f"Total realized value: ${sum(values):,.2f}")
print(f"Mean multiplier: {np.mean(multipliers):.3f}×")
print(f"Final stability: {phi_stabs[-1]:.3f}  ({solver.numerical_stability_threshold(values[-1]/1e6)[1]})")