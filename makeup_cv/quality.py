
import numpy as np

class QualityMonitor:
    def deltaE_map(self, target_uv: np.ndarray, predicted_uv: np.ndarray) -> np.ndarray:
        # Placeholder; plug CIEDE2000 in practice
        return np.abs(target_uv - predicted_uv)

    def coverage_pct(self, target_uv: np.ndarray, predicted_uv: np.ndarray, tol: float=0.1) -> float:
        want = target_uv > 0
        hit  = np.abs(predicted_uv - target_uv) <= tol
        denom = max(1, int(want.sum()))
        return float((want & hit).sum()) / float(denom)
