
import numpy as np
from typing import Tuple
from .types import DesignTargets

class DesignBuilder:
    """Turns a reference picture/AI look into UV-space targets and masks.
    For MVP demo, synthesize a cheek gradient in UV.
    """
    def __init__(self, uv_resolution: Tuple[int,int]=(256,256)):
        self.uv_res = uv_resolution

    def parse_reference(self, ref_rgb: np.ndarray) -> dict:
        # TODO: Replace with actual parsing (SegFormer/BiSeNet) of reference look
        return { "palette": {"cheek": [0.9]} }

    def to_uv_targets(self, user_mesh_uv: np.ndarray, parsed_ref: dict) -> DesignTargets:
        H, W = self.uv_res
        # Build a simple two-cheek target in UV: left at (0.35,0.55), right at (0.65,0.55)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        u = xx / max(W-1,1); v = yy / max(H-1,1)
        centers = [(0.35,0.55),(0.65,0.55)]
        sigma = 0.08
        target = np.zeros((H,W), dtype=np.float32)
        for cu,cv in centers:
            target += np.exp(-((u-cu)**2 + (v-cv)**2)/(2*sigma**2))
        target = np.clip(target / target.max(), 0, 1)

        cheek_mask = (target > 0.05).astype(np.uint8)
        return DesignTargets(
            target_uv=target,
            cheek_mask_uv=cheek_mask,
            hair_mask_uv=np.zeros_like(cheek_mask, np.uint8),
            keepout_mask_uv=np.zeros_like(cheek_mask, np.uint8),
            geodesic_dist_mm=None
        )

    def spray_kernel_sigma_mm(self, standoff_mm: float) -> float:
        a, b = 0.07, 0.0
        return a*standoff_mm + b
