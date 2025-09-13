
# Cheek Airbrush MVP — Design Plan (CV-only, Mesh-Centric)

## 0) Purpose & scope
**Goal:** Deliver a non-contact **cheek airbrush** MVP that plans in **UV space** on a **personalized face mesh**, re-targets to 3D each frame, and outputs **spray footprints** and **CV safety events** to the control layer.  
**Out of scope:** Robot motion planning/control, eyes/mascara/lash tools, lip contact tools.

## 1) System overview
**Inputs (per frame):** RGB (30–60 FPS), RGB-D (30–60 FPS), reference look (photo or preset).  
**Core CV modules:**
1) **Mesh fitting & tracking:** DECA/FLAME (or SynergyNet→FLAME) personalized mesh; rigid ICP update (optional local non-rigid on cheek patch).  
2) **Design → UV targets:** Parse look (SegFormer/BiSeNet) → cheek **target density map** in UV (T_uv).  
3) **UV planning:** Raster centers (zig-zag) with base intensities.  
4) **Per-frame retargeting:** UV→mesh(t)→world; compute **spray footprints** (center, normal, σ(Z), intensity).  
5) **Tool tracking:** Fiducial (AprilTag/ArUco) + depth refinement → nozzle tip & axis.  
6) **Safety monitors (CV):** motion spikes, nozzle keep-out/tilt, standoff error, overspray risk.  
7) **Preview & residuals:** AR overlay, ΔE*ab and coverage estimators.

**Outputs:**  
- `spray_footprints_world[t]` (list of center_world, normal_world, standoff_mm, sigma_mm, intensity_0_1)  
- `cv_safety_events[t]` (motion spike, overspray risk, nozzle tilt/keep-out, standoff/speed flags)

## 2) Data flow
```
Reference Look ──► Design Parser ──► UV Targets (T_uv, cheek_mask_uv)
                                     │
           RGB-D ─► Mesh Fit (DECA init) ─► Mesh_t (V_t,F,UV,N) ─► Retarget UV→3D each frame
                                     │                                 │
                                     └────────► UV Raster Planner ◄────┘
RGB-D ─► Tool Tracking (fiducial) ─► Nozzle Pose  ─► Safety Monitors ─► Events
```

## 3) Personalized mesh & live tracking
- **Initial:** Fit DECA/FLAME (or SynergyNet→FLAME) → `(V0,F,UV,N)`, `T_world_head = I`.  
- **Tracking (60–120 Hz):** Rigid ICP (Open3D) aligns live RGB-D to the mesh; publish `T_world_head(t)`.  
- **Optional local non-rigid:** Small ARAP/CPD warp on cheek vertices (10–20 Hz) for soft tissue motion.

**Frames:** `{head}` is mesh-local; vertices `V_t` live in `{head}`; world transform `T_world_head(t)` gives `{world}`.

## 4) Design → UV targets
- **Parsing the look:** SegFormer/BiSeNet on the **reference** (or use presets). Extract cheek region & target color (CIE Lab).  
- **Target map:** Build `T_uv` (0..1). For MVP, an elliptical Gaussian around malar prominence (per cheek).  
- **Hair/no-go masks:** Hair, eyes, nostrils → project to UV.  
- **Geodesic distances:** Heat-method geodesics on mesh → distance to hair boundary for soft flow gating.

## 5) UV planning (cheek only)
- **Rasterization:** Zig-zag lines in UV with spacing `s_uv ≈ 0.8·σ(Z*) / face_UV_scale`.  
- **Points:** `PlannedUVPoint{ uv=(u,v), base_intensity }` sampled along rasters.  
- **Boundary shaping:** Reduce intensity near hair/no-go by geodesic distance.

## 6) Per-frame retargeting
For each planned UV point at time `t`:
1) UV→triangle lookup (`UV,F`) → barycentric weights.  
2) Interpolate `p_mesh`, `n_mesh` on `(V_t,N_t)`.  
3) World pose: `p_world = T_world_head(t)·p_mesh`, `n_world = R_world_head(t)·n_mesh`.  
4) Standoff `d` (e.g., 40 mm): **nozzle target** = `p_world + d·n_world`.  
5) **σ(Z):** plume width from calibrated `σ(Z)=a·Z+b` (Z from depth at `p_world`).  
6) **Intensity gating:** `gate = clip(geo_dist / margin_mm, 0..1)`; `intensity = base * gate`.  
7) Emit **SprayFootprint** with center, normal, σ, standoff, intensity.

## 7) Tool tracking (vision only)
- **Primary:** AprilTag/ArUco on airbrush → `solvePnP` → `T_world_tool`.  
- **Tip & axis:** Apply tip offset; axis from tag; refine by 3D line fit in local depth; compute speed by filtered diff.

## 8) Safety monitoring (CV signals)
- **Motion spike:** from `ΔT_world_head` over 100 ms; thresholds e.g., > **5 mm** or > **7°**.  
- **Nozzle keep-out/tilt:** distance to eye/nose keep-outs on mesh; tilt > **15°** flag.  
- **Standoff error:** |actual – target| > **5 mm**.  
- **Overspray risk:** footprint ellipse overlaps hair/no-go in UV by > **0.5%** area.

## 9) Preview & residuals
- **Preview:** simulate deposition from footprints in UV; overlay on RGB via mesh texture.  
- **Residual UV:** `R_uv = T_uv − D̂_uv` (accumulated predicted deposition) for corrective passes.

## 10) Interfaces (to control)
- `spray_footprints_world[t]` (list of `SprayFootprint`)  
- `cv_safety_events[t]` (`Events{...}`)  
- Optional: `residual_uv`, preview frames

## 11) Initial configuration
- `standoff_mm=40`, `max_tilt_deg=15`, `hair_margin_mm=8`  
- `σ(Z)=0.07·Z` (calibrate)  
- Motion spike: `>5 mm` or `>7°` in `100 ms`  
- Overspray overlap threshold: `0.5%`

## 12) Risks & mitigations
- **Depth noise near hairline:** bilateral/median filtering; mesh geodesic gating; conservative margins.  
- **Mask flicker:** optical-flow warp + EMA smoothing.  
- **Fiducial loss:** quality threshold; depth-based cylinder line fit cross-check.  
- **ICP drift:** periodic re-init; add landmark PnP prior; fuse IMU if available.

## 13) Milestones
- M1: Dummy mesh + UV pipeline + deposition sim/preview  
- M2: Live ICP + retarget @ 60 Hz; tool track stub  
- M3: Safety monitors & overlay; residual maps  
- M4: Calibration (σ(Z), flow PWM) + dry run (dummy head)  
- M5: Wet runs (board, dummy head) → hit KPIs (see test plan)
