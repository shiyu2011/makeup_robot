
import numpy as np
from typing import List, Tuple
from .config import CVConfig
from .types import MeshState, DesignTargets, PlannedUVPoint, SprayFootprint, Events
from .mesh_fit import MeshFitter
from .design import DesignBuilder
from .hair_masks import OcclusionUV
from .planning import SprayPlannerUV
from .retarget import Retargeter
from .tool_tracking import ToolTracker, ToolPose
from .safety import SafetyMonitor
from .quality import QualityMonitor
from .preview import PreviewRenderer

class MakeupCVPipeline:
    def __init__(self, cfg: CVConfig):
        self.cfg = cfg
        self.mesh_fit   = MeshFitter()
        self.design     = DesignBuilder(uv_resolution=(256,256))
        self.occ_uv     = OcclusionUV()
        self.planner_uv = SprayPlannerUV(spacing_uv=0.02)
        self.retarget   = Retargeter(cfg)
        self.tool_track = ToolTracker(tip_offset_tool=np.array([0.0,0.0,0.03], dtype=np.float32))  # 3cm forward
        self.safety     = SafetyMonitor(cfg)
        self.quality    = QualityMonitor()
        self.preview    = PreviewRenderer()

        self.mesh: MeshState = None
        self.targets: DesignTargets = None
        self.planned: List[PlannedUVPoint] = []
        self.predicted_uv_accum = None  # running deposition in UV

    # ---- Offline steps (once per session) ----
    def build_personalized_mesh(self, rgb0, depth0):
        self.mesh = self.mesh_fit.fit_initial(rgb0, depth0)

    def build_design_targets(self, reference_rgb):
        parsed = self.design.parse_reference(reference_rgb)
        self.targets = self.design.to_uv_targets(self.mesh.UV, parsed)
        # Geodesics are optional; for now, None indicates no gating map.

    def plan_uv_paths(self):
        self.planned = self.planner_uv.rasterize_cheek(self.targets)
        return self.planned

    # ---- Runtime loop (each frame) ----
    def step(self, rgb, depth):
        # 1) Update mesh pose (ICP stub)
        self.mesh = self.mesh_fit.update_with_icp(self.mesh, rgb, depth)

        # 2) Tool pose (stubbed)
        tool_pose: ToolPose = self.tool_track.detect(rgb, depth)

        # 3) Retarget planned UV points to current mesh; geodesic gating
        def gate_fn(uv):
            return 1.0  # TODO: use geodesic distances to hair/keepout in UV
        footprints: List[SprayFootprint] = self.retarget.make_footprints(self.mesh, self.planned, gate_fn)

        # 4) Safety checks (CV only)
        ev_motion = self.safety.motion_spike(self.mesh.T_world_head)
        ev_keep   = self.safety.nozzle_keepout(min_dist_mm=999.0, tilt_deg=0.0) # TODO
        ev_speed  = self.safety.standoff_speed(standoff_err_mm=0.0, speed_mm_s=tool_pose.speed_mm_s)

        ev = Events()
        for k,v in {**ev.__dict__, **ev_motion.__dict__, **ev_keep.__dict__, **ev_speed.__dict__}.items():
            setattr(ev, k, v)

        return footprints, ev
