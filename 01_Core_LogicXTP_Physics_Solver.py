import sympy as sp
import numpy as np
from typing import Tuple

class XTP_PhysicsSolver:
    """Symbolic & numerical solver for the coupled Dirac-market Lagrangian."""
    def __init__(self):
        # Symbols
        self.phi, self.t = sp.symbols('phi t')
        self.phi_t = sp.Derivative(self.phi, self.t)
        self.m, self.lam, self.phi0, self.eta = sp.symbols('m lambda phi_0 eta', real=True, positive=True)
        self.V_mkt = sp.Function('V_mkt')(self.t)
        
        # Scalar approximation of the effective Lagrangian (Higgs + market coupling)
        kinetic = sp.Rational(1,2) * self.phi_t**2
        potential = (self.m**2 / 2) * self.phi**2 + self.lam * (self.phi**2 - self.phi0**2)**2
        coupling = self.eta * self.V_mkt * self.phi**2
        
        self.L: sp.Expr = kinetic - potential - coupling

    def get_euler_lagrange(self) -> sp.Expr:
        """Returns symbolic Euler-Lagrange equation (scalar approx)."""
        dL_dphi = sp.diff(self.L, self.phi)
        dL_dphit = sp.diff(self.L, self.phi_t)
        EL = dL_dphi - sp.diff(dL_dphit, self.t)
        return EL.doit().simplify()

    def numerical_stability_threshold(
        self,
        V_mkt_current: float,
        m: float = 1.0,
        lam: float = 0.1,
        phi0: float = 1.0,
        eta: float = 0.05
    ) -> Tuple[float, str]:
        """
        Approximate stationary point |phi| and stability message.
        Solves effective potential minimum numerically.
        """
        def Veff(phi_val):
            return (m**2 / 2) * phi_val**2 + lam * (phi_val**2 - phi0**2)**2 + eta * V_mkt_current * phi_val**2
        
        from scipy.optimize import minimize_scalar
        res = minimize_scalar(Veff, bounds=(-2*phi0, 2*phi0), method='bounded')
        
        if res.success:
            phi_min = np.sqrt(res.x**2)  # magnitude
            if phi_min > 0.8 * phi0:
                status = "Stable Stationary Trail (high liquidity support)"
            elif phi_min > 0.3 * phi0:
                status = "Marginal stability – adjust voltage upward"
            else:
                status = "Trail evaporation risk – increase market coupling or V"
            return phi_min, status
        return 0.0, "Solver failed – check parameters"