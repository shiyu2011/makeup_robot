
import numpy as np
from makeup_cv.config import CVConfig
from makeup_cv.pipeline import MakeupCVPipeline
from makeup_cv.mesh_fit import create_dummy_mesh

def main():
    cfg = CVConfig()
    pipe = MakeupCVPipeline(cfg)

    # Dummy inputs
    rgb0  = np.zeros((480,640,3), np.uint8)
    depth0= np.zeros((480,640), np.float32)

    # Build personalized mesh (dummy) and targets
    pipe.mesh = create_dummy_mesh()
    ref = np.zeros((480,640,3), np.uint8)
    pipe.build_design_targets(ref)
    planned = pipe.plan_uv_paths()
    print(f"Planned UV points: {len(planned)} (showing first 5)\n", planned[:5])

    # One runtime step (no real camera)
    rgb = np.zeros((480,640,3), np.uint8)
    depth = np.zeros((480,640), np.float32)
    footprints, events = pipe.step(rgb, depth)

    print("\nFootprints (first 5):")
    for fp in footprints[:5]:
        print(fp)

    print("\nEvents:", events)

if __name__ == "__main__":
    main()
