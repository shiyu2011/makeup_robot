
import numpy as np
from typing import List, Tuple
from .types import MeshState, PlannedUVPoint, SprayFootprint
from .config import CVConfig

def _barycentric_2d(p, a, b, c):
    """Compute barycentric coordinates of p wrt triangle (a,b,c) in 2D."""
    v0 = b - a; v1 = c - a; v2 = p - a
    d00 = (v0*v0).sum(); d01 = (v0*v1).sum(); d11 = (v1*v1).sum()
    d20 = (v2*v0).sum(); d21 = (v2*v1).sum()
    denom = d00 * d11 - d01 * d01
    if abs(denom) < 1e-12:
        return None
    v = (d11 * d20 - d01 * d21) / denom
    w = (d00 * d21 - d01 * d20) / denom
    u = 1.0 - v - w
    return np.array([u,v,w], dtype=np.float32)

class UVBaryIndex:
    """Naive UV->triangle lookup for small meshes (O(M) per query)."""
    def __init__(self, UV: np.ndarray, F: np.ndarray):
        self.UV = UV
        self.F = F

    def lookup(self, uv: Tuple[float,float]):
        p = np.array([uv[0], uv[1]], dtype=np.float32)
        for tidx, tri in enumerate(self.F):
            a = self.UV[tri[0]]; b = self.UV[tri[1]]; c = self.UV[tri[2]]
            bc = _barycentric_2d(p, a, b, c)
            if bc is None: 
                continue
            if (bc >= -1e-5).all() and (bc <= 1+1e-5).all():
                return tidx, bc
        # Fallback: clamp to first tri
        return 0, np.array([1.0, 0.0, 0.0], dtype=np.float32)

class Retargeter:
    """Maps planned UV pass centers to current mesh pose; computes current spray footprints."""
    def __init__(self, cfg: CVConfig):
        self.cfg = cfg
        self._uv_index: UVBaryIndex = None

    def _ensure_index(self, mesh: MeshState):
        if self._uv_index is None:
            self._uv_index = UVBaryIndex(mesh.UV, mesh.F)

    def uv_to_mesh_point_normal(self, mesh: MeshState, uv: tuple) -> tuple:
        self._ensure_index(mesh)
        tidx, bc = self._uv_index.lookup(uv)
        tri = mesh.F[tidx]
        V = mesh.V[tri]  # (3,3)
        N = mesh.N[tri] if mesh.N is not None else np.array([[0,0,1]]*3, dtype=np.float32)
        p = (bc[0]*V[0] + bc[1]*V[1] + bc[2]*V[2]).astype(np.float32)
        n = (bc[0]*N[0] + bc[1]*N[1] + bc[2]*N[2]).astype(np.float32)
        if np.linalg.norm(n) < 1e-9:
            n = np.array([0,0,1], dtype=np.float32)
        else:
            n = n / np.linalg.norm(n)
        return p, n

    def make_footprints(self, mesh: MeshState, planned: List[PlannedUVPoint], geodesic_gate_fn) -> List[SprayFootprint]:
        fps: List[SprayFootprint] = []
        self._ensure_index(mesh)
        # sigma from standoff (simple linear model)
        sigma = self.cfg.sigma_linear_a*self.cfg.standoff_mm + self.cfg.sigma_linear_b
        R = mesh.T_world_head[:3,:3]
        t = mesh.T_world_head[:3, 3]

        for p in planned:
            p_mesh, n_mesh = self.uv_to_mesh_point_normal(mesh, p.uv)

            p_skin_world = (R @ p_mesh.reshape(3,1) + t.reshape(3,1)).ravel()
            n_world = (R @ n_mesh.reshape(3,1)).ravel()
            if np.linalg.norm(n_world) < 1e-9:
                n_world = np.array([0,0,1.0], dtype=np.float32)
            else:
                n_world = n_world / np.linalg.norm(n_world)

            intensity = float(np.clip(p.base_intensity_0_1 * float(geodesic_gate_fn(p.uv)), 0.0, 1.0))
            fps.append(SprayFootprint(
                uv=p.uv,
                center_world=p_skin_world.astype(np.float32),
                normal_world=n_world.astype(np.float32),
                standoff_mm=self.cfg.standoff_mm,
                sigma_mm=sigma,
                ellipse_axes_mm=(float(sigma*1.414), float(sigma*1.414)),
                intensity_0_1=intensity,
                quality=1.0
            ))
        return fps
