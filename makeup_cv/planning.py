
import numpy as np
from typing import List, Tuple
from .types import DesignTargets, PlannedUVPoint

class SprayPlannerUV:
    """Converts UV target map into discrete pass centers & base intensities in UV."""
    def __init__(self, spacing_uv: float=0.02):
        self.spacing_uv = spacing_uv

    def rasterize_cheek(self, targets: DesignTargets) -> List[PlannedUVPoint]:
        H, W = targets.target_uv.shape
        du = self.spacing_uv
        dv = self.spacing_uv

        # Generate a simple zig-zag over the cheek mask bounding box
        ys, xs = np.where(targets.cheek_mask_uv > 0)
        if ys.size == 0:
            return []
        y0, y1 = ys.min(), ys.max()
        x0, x1 = xs.min(), xs.max()

        u0, u1 = x0/(W-1), x1/(W-1)
        v0, v1 = y0/(H-1), y1/(H-1)

        u_samples = np.arange(u0, u1+1e-6, du)
        v_samples = np.arange(v0, v1+1e-6, dv)

        points: List[PlannedUVPoint] = []
        flip = False
        for v in v_samples:
            if flip:
                u_iter = u_samples[::-1]
            else:
                u_iter = u_samples
            for u in u_iter:
                x = min(W-1, max(0, int(round(u*(W-1)))))
                y = min(H-1, max(0, int(round(v*(H-1)))))
                if targets.cheek_mask_uv[y,x] == 0:
                    continue
                intensity = float(targets.target_uv[y,x])
                if intensity <= 1e-3:
                    continue
                points.append(PlannedUVPoint(uv=(float(u), float(v)), base_intensity_0_1=intensity))
            flip = not flip
        return points

    def lips_outline_fill(self, targets: DesignTargets) -> List[PlannedUVPoint]:
        # TODO: sample outline curve then offset contours in UV
        return []
