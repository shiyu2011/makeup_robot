
import numpy as np
from .types import Events
from .config import CVConfig

class SafetyMonitor:
    def __init__(self, cfg: CVConfig):
        self.cfg = cfg
        self._prev_T = None

    def motion_spike(self, T_curr: np.ndarray) -> Events:
        e = Events()
        if self._prev_T is None:
            self._prev_T = T_curr.copy()
            return e
        T_prev = self._prev_T
        dt_mm = float(np.linalg.norm(T_curr[:3,3] - T_prev[:3,3]) * 1000.0)  # m→mm if inputs in meters
        R = T_prev[:3,:3].T @ T_curr[:3,:3]
        ang = float(np.degrees(np.arccos(np.clip((np.trace(R)-1)/2.0, -1.0, 1.0))))
        if dt_mm > self.cfg.motion_spike_mm or ang > self.cfg.motion_spike_deg:
            e.motion_spike = True
            e.motion_dt_mm = dt_mm
            e.motion_dtheta_deg = ang
        self._prev_T = T_curr.copy()
        return e

    def nozzle_keepout(self, min_dist_mm: float, tilt_deg: float) -> Events:
        e = Events()
        e.nozzle_near_keepout = (min_dist_mm < self.cfg.nozzle_keepout_min_mm)
        e.nozzle_tilt_excess  = (tilt_deg > self.cfg.max_tilt_deg)
        return e

    def standoff_speed(self, standoff_err_mm: float, speed_mm_s: float) -> Events:
        e = Events()
        e.standoff_violation = (abs(standoff_err_mm) > self.cfg.standoff_tolerance_mm)
        e.speed_violation    = (speed_mm_s > self.cfg.safety_speed_cap_mm_s)
        return e
