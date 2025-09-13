
import numpy as np
from dataclasses import dataclass

@dataclass
class ToolPose:
    T_world_tool: np.ndarray  # 4x4
    tip_world: np.ndarray     # (3,)
    axis_world: np.ndarray    # (3,)
    speed_mm_s: float
    quality: float

class ToolTracker:
    """Fiducial (AprilTag/ArUco) + depth refinement → nozzle pose.
    This is a stub that returns a static pose for scaffolding.
    """
    def __init__(self, tip_offset_tool: np.ndarray):
        self.tip_offset_tool = tip_offset_tool
        self._prev_tip = None

    def detect(self, rgb: np.ndarray, depth: np.ndarray) -> ToolPose:
        T = np.eye(4, dtype=np.float32)
        axis_world = np.array([0,0,-1.0], dtype=np.float32)
        tip_world = (T[:3,:3] @ self.tip_offset_tool.reshape(3,1) + T[:3,3:4]).ravel()
        speed = 0.0
        if self._prev_tip is not None:
            speed = float(np.linalg.norm(tip_world - self._prev_tip) * 1000.0)  # m→mm if inputs were meters
        self._prev_tip = tip_world.copy()
        return ToolPose(T_world_tool=T, tip_world=tip_world, axis_world=axis_world, speed_mm_s=speed, quality=0.5)
