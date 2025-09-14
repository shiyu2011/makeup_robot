
# Cheek Airbrush MVP — Design Plan (CV-only, Mesh-Centric, v2)

## 0) Purpose & scope
Deliver a **non-contact cheek airbrush MVP** that:
- Builds a **personalized face mesh**,
- Creates a **cheek color target** by either **UV-based planning** (for 2D designs) or **pure 3D parametric planning**,
- Runs **real-time, per-frame retargeting** using **depth + ICP** (no UV needed at runtime),
- Outputs **spray footprints** and **CV safety events** to the control layer.

> Out of scope: robot motion planning/control, eyes/mascara/lash tools, contact tools.

---

## 1) System overview
**Inputs (per frame):** RGB (30–60 FPS), RGB-D (30–60 FPS). Reference look (optional 2D design image/preset).

**Core CV modules:**
1) **Personalized mesh + tracking:** DECA/FLAME init; **ICP** (point-to-plane) for live pose.  
2) **Planning (one-time pre-spray):**  
   - **UV-based** (if mapping a 2D design): build cheek target in UV.  
   - **3D parametric** (if no 2D design): define cheek ellipses/gradients directly on mesh.  
3) **Per-frame retargeting (real-time):** **transform planned 3D reference points** with current head pose; compute spray footprints (center, normal, σ(Z), intensity).  
4) **Tool tracking (vision):** fiducial + depth refinement → nozzle pose (for monitoring).  
5) **Safety monitors (CV):** motion spikes, keep-out/tilt, standoff error, overspray risk.  
6) **Preview & residuals:** AR overlay and ΔE/coverage estimators (optional UI).

**Outputs:**  
- `spray_footprints_world[t]` (center_world, normal_world, standoff_mm, sigma_mm, intensity_0_1)  
- `cv_safety_events[t]` (motion_spike, overspray_risk, nozzle tilt/keep-out, standoff/speed)

---

## 2) Data flow (planning vs real-time)

```
         (Optional 2D Design)                 (Parametric 3D Design)
Reference Look ──► Parse & UV map ──┐      ┌─► Define cheek ellipses/gradients in 3D
                                    └─► Cheek Target (reference points on mesh, with base intensities)
                                                │
        RGB-D ──► Mesh Init (DECA/FLAME) ─► Personalized Mesh (V,F,UV,N)
        RGB-D ──► ICP (60–120 Hz) ────────► T_world←head(t)
                                                │
                   Per-frame Retargeting (no UV): apply T_world←head(t) to reference 3D points
                                                │
                Spray Footprints (center, normal, σ(Z), intensity)  +  CV Safety Events
```

**Key point:** UV is used only if you *plan* from a 2D design. **Per-frame retargeting uses ICP pose only** (direct 3D rigid transform; no optimization, no UV lookup).

---

## 3) Personalized mesh & tracking
- **Initial personalization:** fit DECA/FLAME (or SynergyNet→FLAME) → `(V0,F,UV,N)` in `{head}`; set `T_world←head = I`.  
- **Live tracking (60–120 Hz):** ICP (point-to-plane) between current RGB-D point cloud and the mesh to update `T_world←head(t)`.  
- **Optional local non-rigid:** small ARAP/CPD warp on cheek vertices at 10–20 Hz for soft tissue drift (not required for MVP).

Frames: vertices live in `{head}`; world pose given by `T_world←head(t)`.

---

## 4) Planning (one-time pre-spray)

### A) UV-based planning (use when transferring a 2D design)
1. Parse reference (SegFormer/BiSeNet) → cheek mask & target color (CIE Lab).  
2. Build `T_uv` (0..1) cheek map; optionally shape gradient.  
3. Raster centers in **UV** (zig-zag) → back-project to **reference 3D points** on the mesh (one-time).  
4. Save **reference 3D points + base intensities** (these are the only inputs used at runtime).

### B) 3D parametric planning (no UV; use when you don’t need a 2D design)
1. Define cheek region by 3D landmarks (malar prominence, cheekbone line).  
2. Create **elliptical/teardrop gradient** on the mesh surface (geodesic coordinates).  
3. Sample **reference 3D raster centers** with base intensities directly on the mesh.  
4. Save **reference 3D points + base intensities**.

> In both cases, after planning you possess **reference 3D points** on the mesh with base intensities. Real-time uses only these and the ICP pose.

---

## 5) Deposition model (calibrated offline)
Gaussian plume (lateral spread) as a function of standoff:
\[
\sigma(Z) \approx a \cdot Z + b,\quad
D(r) = \frac{k \cdot \text{flow}}{\text{speed}} \cos\theta \cdot \exp\Big(-\frac{r^2}{2\sigma(Z)^2}\Big)
\]
Where \(Z\)=standoff, \(\theta\)=angle to surface normal.

---

## 6) **Per-frame retargeting (real-time, no UV, no optimization)**
For each **reference 3D point** \(p^{ref}\) on the mesh with base intensity \(I_{base}\):

1) **Transform to world** using the current ICP pose:  
\[
p_{world}(t) = R_{head}(t)\,p^{ref} + t_{head}(t)
\]
Likewise transform the stored surface normal \(n^{ref}\):  
\[
n_{world}(t) = R_{head}(t)\,n^{ref}
\]

2) **Nozzle target (standoff \(d\))**:  
\[
p_{nozzle}(t) = p_{world}(t) + d \cdot n_{world}(t)
\]

3) **Plume width** from current standoff (sample Z at \(p_{world}\) from depth if needed):  
\[
\sigma(Z(t)) = a \cdot Z(t) + b
\]

4) **Intensity gating** (safety & quality):  
- Compute **geodesic distance** on the mesh to hair/keep-out boundary: \(d_{\text{geo}}\).  
- Gate: \(g = \mathrm{clip}(d_{\text{geo}} / \text{margin}_{mm}, 0, 1)\).  
- Final intensity: \(I(t) = I_{base} \cdot g\).

5) **Emit `SprayFootprint`**  
`{ center_world=p_world, normal_world=n_world, standoff_mm=d, sigma_mm=σ(Z), intensity_0_1=I(t) }`

> This is a **direct computation each frame** (rigid transform + lookup). **No UV** and **no optimization** are required at runtime.

---

## 7) Tool tracking (vision only; monitoring)
- **Primary:** AprilTag/ArUco on the airbrush → `solvePnP` → `T_world←tool`.  
- **Tip & axis:** tip offset; axis from tag; depth line fit for refinement; speed by filtered diff.  
- Used for **safety checks** (standoff, tilt, proximity), not for planning.

---

## 8) Safety monitoring (CV signals)
- **Motion spike:** from `ΔT_world←head` over 100 ms (e.g., >5 mm or >7°).  
- **Nozzle keep-out/tilt:** distance to eye/nose keep-outs on the mesh; tilt >15° flag.  
- **Standoff error:** |actual − target| > 5 mm.  
- **Overspray risk:** footprint ellipse overlaps hair/keep-out by >0.5% area.

All events published as `cv_safety_events[t]`; the controller decides pause/retract.

---

## 9) Preview & residuals
- **Preview:** simulate deposition from footprints; overlay on RGB via mesh texturing (optional UI).  
- **Residual UV/3D:** tracked predicted coverage vs target; schedule corrective micro-passes if needed.

---

## 10) Interfaces (to control layer)
- `spray_footprints_world[t]`: list of footprints {center_world, normal_world, standoff_mm, sigma_mm, intensity_0_1}.  
- `cv_safety_events[t]`: `Events{motion_spike, overspray_risk, nozzle_tilt_excess, nozzle_near_keepout, standoff_violation, speed_violation}`.  
- Optional: `predicted_coverage`, preview frames.

---

## 11) Initial configuration
- `standoff_mm=40`, `max_tilt_deg=15`, `hair_margin_mm=8`  
- `σ(Z)=0.07·Z` (calibrate)  
- Motion spike: `>5 mm` or `>7°` in `100 ms`  
- Overspray overlap threshold: `0.5%`

---

## 12) Risks & mitigations
- **Depth noise near hairline:** bilateral/median filter; conservative geodesic margins.  
- **Mask flicker (if UV planning used):** optical-flow warp + EMA smoothing.  
- **Fiducial loss:** quality thresholds; depth cylinder fit cross-check.  
- **ICP drift/failure:** re-seed from previous frame; add sparse 3D landmarks; small motion constraints.

---

## 13) Milestones
- M1: Parametric 3D planning path + deposition sim/preview  
- M2: ICP pose @ 60–120 Hz; per-frame retargeting loop (no UV)  
- M3: Safety monitors + tool tracking (monitoring only)  
- M4: σ(Z) & flow calibration; dry runs on dummy head  
- M5: Wet runs (board & dummy head) → hit accuracy/effectiveness/safety KPIs
