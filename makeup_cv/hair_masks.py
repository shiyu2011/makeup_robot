
import numpy as np
from .types import MeshState, DesignTargets

class OcclusionUV:
    """Build UV-space hair & keepout masks; compute geodesic distances for gating."""
    def __init__(self):
        pass

    def masks_to_uv(self, mesh: MeshState, hair_mask_img: np.ndarray, keepout_img: np.ndarray) -> DesignTargets:
        # TODO: Project image masks to UV using rasterization / barycentric map
        raise NotImplementedError("Projecting image-space masks to UV not implemented in scaffold.")

    def geodesic_distance_mm(self, mesh: MeshState, hair_boundary_uv=None):
        # TODO: Replace with heat-method geodesics on the mesh; here, return None
        return None
