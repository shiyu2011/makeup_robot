
import numpy as np
from .types import MeshState

def _identity_pose():
    T = np.eye(4, dtype=np.float32)
    return T

def create_dummy_mesh() -> MeshState:
    """Create a small quad mesh patch with UVs as a placeholder face region."""
    # 2x2 grid -> 4 verts -> 2 triangles (very coarse for demo)
    V = np.array([
        [-0.05, -0.05, 0.0],
        [ 0.05, -0.05, 0.0],
        [-0.05,  0.05, 0.0],
        [ 0.05,  0.05, 0.0],
    ], dtype=np.float32)
    F = np.array([[0,1,2],[2,1,3]], dtype=np.int32)
    UV = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
    ], dtype=np.float32)
    N = np.tile(np.array([0.0,0.0,1.0], dtype=np.float32), (V.shape[0],1))
    return MeshState(V=V, F=F, UV=UV, N=N, T_world_head=_identity_pose())

class MeshFitter:
    """Fits personalized mesh once; updates pose per frame (stub ICP)."""
    def __init__(self):
        pass

    def fit_initial(self, rgb: np.ndarray, depth: np.ndarray) -> MeshState:
        # TODO: Replace with DECA/FLAME fitting and initialize T_world_head
        return create_dummy_mesh()

    def update_with_icp(self, prev: MeshState, rgb: np.ndarray, depth: np.ndarray) -> MeshState:
        # TODO: Replace with RGB-D ICP to update T_world_head (and local deformations if desired)
        # For demo, return prev unchanged.
        return prev
