
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np

Vec3 = np.ndarray  # shape (3,)
Mat4 = np.ndarray  # shape (4,4)

@dataclass
class MeshState:
    """Personalized face mesh at time t."""
    V: np.ndarray            # (N,3) vertices in head frame
    F: np.ndarray            # (M,3) triangle indices (int)
    UV: np.ndarray           # (N,2) per-vertex UV in [0,1]
    N: Optional[np.ndarray]  # (N,3) per-vertex normals
    T_world_head: Mat4       # world<-head transform 4x4

@dataclass
class SprayFootprint:
    """One instantaneous spray 'stamp' predicted at time t."""
    uv: Tuple[float, float]
    center_world: Vec3
    normal_world: Vec3
    standoff_mm: float
    sigma_mm: float
    ellipse_axes_mm: Tuple[float, float]
    intensity_0_1: float
    quality: float = 1.0  # confidence

@dataclass
class PlannedUVPoint:
    """Planned pass center in UV space (pre-runtime)."""
    uv: Tuple[float, float]
    base_intensity_0_1: float

@dataclass
class Events:
    motion_spike: bool = False
    motion_dt_mm: float = 0.0
    motion_dtheta_deg: float = 0.0
    blink: bool = False
    squint: bool = False
    yawn: bool = False
    nozzle_near_keepout: bool = False
    nozzle_tilt_excess: bool = False
    overspray_risk: bool = False
    standoff_violation: bool = False
    speed_violation: bool = False

@dataclass
class DesignTargets:
    """Design in UV space (textures/masks)."""
    target_uv: np.ndarray                           # HxW float32 desired density/intensity [0..1]
    lips_outline_uv: Optional[List[Tuple[float,float]]] = None
    lips_fill_uv: Optional[np.ndarray] = None       # HxW mask
    cheek_mask_uv: Optional[np.ndarray] = None      # HxW mask
    hair_mask_uv: Optional[np.ndarray] = None       # HxW mask
    keepout_mask_uv: Optional[np.ndarray] = None    # HxW mask
    geodesic_dist_mm: Optional[np.ndarray] = None   # HxW or per-vertex distances
