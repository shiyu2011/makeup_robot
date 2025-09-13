
import numpy as np

class PreviewRenderer:
    def render_prediction_overlay(self, rgb: np.ndarray, mesh, footprints: list) -> np.ndarray:
        """Project current footprints onto image to visualize predicted deposition.
        This is a placeholder; implement camera projection + ellipse drawing here.
        """
        return rgb

    def render_before_after(self, rgb: np.ndarray, mesh, targets_uv: np.ndarray, predicted_uv: np.ndarray) -> np.ndarray:
        """Texture-bake UV maps on mesh and overlay. Placeholder."""
        return rgb
