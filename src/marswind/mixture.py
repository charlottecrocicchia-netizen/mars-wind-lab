"""Mass and remanence balance for a declared porous two-solid source.

Density averages a fraction q of source material and (1-q) of nonmagnetic
background with the same matrix and porosity. This is volume bookkeeping,
not a gravity kernel or an inversion for Martian composition.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Mixture:
    matrix_density: float = 2900.
    carrier_density: float = 5180.
    pore_density: float = 0.
    source_fraction: float = 1.
    carrier_remanence: float = 5000.
    coherence: float = 1.

    def __post_init__(self):
        values = (self.matrix_density, self.carrier_density, self.pore_density,
                  self.source_fraction, self.carrier_remanence, self.coherence)
        if not all(math.isfinite(x) for x in values):
            raise ValueError('Finite material parameters are required')
        if not 0 <= self.pore_density < self.matrix_density < self.carrier_density:
            raise ValueError('Require pore density < matrix density < carrier density')
        if not 0 < self.source_fraction <= 1 or not 0 < self.coherence <= 1:
            raise ValueError('Source fraction and coherence must lie in (0, 1]')
        if self.carrier_remanence <= 0:
            raise ValueError('Carrier remanence must be positive')

    @property
    def density_contrast(self):
        return self.carrier_density-self.matrix_density

    def forward(self, solid_fraction, porosity):
        """Return averaged density and magnetization per bulk SOURCE volume."""
        if not 0 <= solid_fraction <= 1 or not 0 <= porosity <= 1:
            raise ValueError('Fractions must lie in [0, 1]')
        bulk_carrier = (1-porosity)*solid_fraction
        density = ((1-porosity)*self.matrix_density+porosity*self.pore_density
                   +self.source_fraction*bulk_carrier*self.density_contrast)
        magnetization = bulk_carrier*self.carrier_remanence*self.coherence
        return density, magnetization

    def inverse(self, density, magnetization):
        """Exact candidate for both equalities; unphysical solutions stay flagged."""
        if not math.isfinite(density) or density <= 0:
            raise ValueError('A positive finite density is required')
        if not math.isfinite(magnetization) or magnetization < 0:
            raise ValueError('A nonnegative finite magnetization is required')
        bulk_carrier = magnetization/(self.carrier_remanence*self.coherence)
        density_cost = self.source_fraction*bulk_carrier*self.density_contrast
        porosity = (self.matrix_density+density_cost-density)/(self.matrix_density-self.pore_density)
        fraction = bulk_carrier/(1-porosity) if porosity < 1 else None
        physical = (-1e-12 <= porosity < 1 and fraction is not None
                    and 0 <= fraction <= 1+1e-12)
        return {'bulk_carrier_fraction_in_source': bulk_carrier,
                'porosity': porosity, 'solid_carrier_fraction_in_source': fraction,
                'density_increment_at_fixed_porosity_kg_m3': density_cost,
                'physical': physical}

    def attainable(self, density, porosity_cap, solid_fraction_cap):
        """Exact attainable interval, varying phi and f inside the given caps.

        In coordinates (phi, b=(1-phi)*f) the constraint is a line segment.
        Both b and M increase with phi along it; its endpoints are analytic.
        """
        if not math.isfinite(density) or density <= 0:
            raise ValueError('A positive finite density is required')
        if not 0 <= porosity_cap < 1 or not 0 <= solid_fraction_cap <= 1:
            raise ValueError('Require 0 <= porosity cap < 1 and 0 <= carrier cap <= 1')
        rm, rp = self.matrix_density, self.pore_density
        effective_solid = rm+self.source_fraction*solid_fraction_cap*self.density_contrast
        low = max(0., (rm-density)/(rm-rp))
        high = min(porosity_cap, (effective_solid-density)/(effective_solid-rp))
        if high < low-1e-12 or high < -1e-12:
            return None
        high = max(low, high)
        b = [max(0., (density-rm+p*(rm-rp))/(self.source_fraction*self.density_contrast))
             for p in [low, high]]
        scale = self.carrier_remanence*self.coherence
        return {'porosity_low': low, 'porosity_high': high,
                'bulk_carrier_low': b[0], 'bulk_carrier_high': b[1],
                'magnetization_low_a_m': b[0]*scale,
                'magnetization_high_a_m': b[1]*scale}
