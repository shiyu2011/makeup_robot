
from dataclasses import dataclass

@dataclass
class CVConfig:
    """Configuration for CV-only stack."""
    # Airbrush geometry & behavior
    standoff_mm: float = 40.0
    max_tilt_deg: float = 15.0
    hair_margin_mm: float = 8.0

    # Motion spike detection
    motion_spike_mm: float = 5.0
    motion_spike_deg: float = 7.0
    motion_spike_window_ms: int = 100

    # Spray footprint sigma model: sigma(Z) ≈ a*Z + b (Z in mm)
    sigma_linear_a: float = 0.07
    sigma_linear_b: float = 0.0

    # Safety
    safety_speed_cap_mm_s: float = 200.0
    standoff_tolerance_mm: float = 5.0
    nozzle_keepout_min_mm: float = 25.0
