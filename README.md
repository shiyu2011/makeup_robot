
# Makeup CV MVP (Mesh-based, CV-only)

This repo contains a **first-level, detailed scaffold** for a mesh-centric makeup CV pipeline:
- Personalize a live face mesh
- Convert a design (reference picture or preset) into **UV-space targets**
- Plan **cheek airbrush** & **lip** patterns in UV
- Re-target the plan each frame onto the live mesh
- Track the airbrush tool (vision-only)
- Emit **CV-side safety** and **quality** signals

> **Note**: This is a **CV-only** stack. Robot planning & control are not included here.
> Many functions are stubs with TODOs; the public interfaces and data types are defined so you can fill in modules incrementally.

## Structure

```
makeup_cv/
  __init__.py
  config.py
  types.py
  mesh_fit.py
  design.py
  hair_masks.py
  planning.py
  retarget.py
  tool_tracking.py
  safety.py
  quality.py
  preview.py
  pipeline.py
demo_main.py
```

## Quick Start (scaffold)

```bash
python demo_main.py  # runs the pipeline with dummy data
```

This will create a dummy mesh, generate dummy UV targets, plan UV points,
and run one `step()` of the pipeline (no camera). It prints out
spray footprints and safety event flags.

## Dependencies (suggested)

- Python 3.9+
- numpy
- (later) OpenCV, Open3D, trimesh, potpourri3d/libigl, PyTorch/ONNXRuntime (for models)

Install core:
```
pip install numpy
```
