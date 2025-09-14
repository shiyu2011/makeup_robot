
# Cheek Airbrush MVP — Test Plan (Accuracy, Effectiveness, Safety)

## 0) Objectives
1) **Accuracy:** Deposition location & color vs target (ΔE*ab); minimal overspray.  
2) **Effectiveness:** Coverage & smooth gradient; robust to micro-motion.  
3) **Safety:** Respect keep-outs; safe standoff/speed; timely response to motion/hair intrusions.

## 1) Test environment
- **Hardware:** RGB (≥30 FPS), RGB-D (≥30 FPS), airbrush (valve PWM + pressure), dummy head, then human pilot.  
- **Lighting:** Constant, CRI ≥ 95, fixed white balance.  
- **Calibrations:** camera intrinsics/extrinsics, hand-eye, tip offset, σ(Z) vs standoff, flow vs PWM.  
- **Artifacts:** color swatches (Lab) and printable cheek masks for board/dummy validation.

## 2) Metrics & acceptance criteria
- **Color accuracy (ΔE*ab):** core cheek ROI ≤ **4.0**; 90th percentile ≤ **5.0**.  
- **Coverage:** ≥ **95%** of cheek mask within ±10% of target intensity.  
- **Overspray:** outside cheek mask ≤ **1.0%** footprint area (per pass); total outside ≤ **0.5%** cheek area.  
- **Geometric accuracy:** gradient centerline within **±2.0 mm**; footprint σ within **±10%** of model.  
- **Standoff:** mean |Z−Z*| ≤ **2 mm**, P95 ≤ **5 mm**.  
- **Motion robustness:** pause within **≤100 ms** when spike > **5 mm / 7°**.  
- **Tool tracking quality (bench):** tag detect ≥ **98%**; pose jitter ≤ **1.0 mm RMS** at 40 mm standoff.

## 3) Test matrix
### A) Bench & board
1. **σ(Z) calibration:** single dots at Z ∈ {30,40,50,60} mm; fit σ vs model (≤10% error).  
2. **Raster uniformity (flat board):** evaluate overlap & coverage CV%.  
3. **Overspray gating:** hair/no-go stencil; verify leakage < **1%** area, smooth falloff.

### B) Dummy Head
4. **Retarget stability:** move ±3 mm / ±3° @ 1 Hz; centerline drift ≤ **1.5 mm**.  
5. **Gradient fidelity:** ΔE*ab ≤ **4.0** in core ROI; coverage ≥ **95%**.  
6. **Hair intrusion:** add hair bundle at boundary; confirm pause/skip/re-queue; leakage ≤ **1%**.

### C) Human pilot
7. **Safety & comfort:** no violations; pause on spikes; resume from checkpoint cleanly.  
8. **Effectiveness:** observer rating of gradient smoothness ≥ **4/5**; ΔE & coverage pass.  
9. **Motion spike response:** quick small turn/smile → pause ≤ **100 ms**; resume OK.

## 4) Procedures
### 4.1 Color/deposition measurement
- Capture RAW or fixed-WB before/after; register to mesh; sample ROIs in UV; compute **CIEDE2000 ΔE**.  
- σ(Z): fit 2D Gaussian to dot; report σ_x, σ_y and residuals.

### 4.2 Coverage & overspray
- Compare predicted vs measured intensity maps; compute **coverage%** within ±10% band.  
- Compute area outside cheek mask above low-density threshold; report **overspray%**.

### 4.3 Safety latency
- Induce motion spike (mechanical jig or subject cue); log frame timestamps and event publish time; verify **< 100 ms** latency.  
- Move fiducial near keep-out boundary; verify **nozzle_near_keepout** triggers when distance < 25 mm.

## 5) Example test cases
**TC-A1: σ(Z) calibration** — Pass if all Z have |σ_meas − σ_model|/σ_model ≤ **10%**.  
**TC-B2: Retarget stability** — Pass if projected centers stay within **±1.5 mm** vs planned 3D after transform.  
**TC-B3: Hair intrusion** — Pass if overspray ≤ **1%** and skip/re-queue logged.  
**TC-C1: Human safety pause** — Pass if pause latency < **100 ms** and resume cleanly.

## 6) Instrumentation & logging
- Per frame: `MeshState`, `spray_footprints_world`, `cv_safety_events`, `tool_pose`, preview frames, ΔE/coverage summaries.  
- Persist calibration curves (σ(Z), flow(PWM)); version control configs & weights.

## 7) Reporting
- KPIs vs thresholds; plots of σ(Z), ΔE distributions, coverage histograms; event timelines.  
- Photo evidence (before/after) and overlays.

## 8) Exit criteria
- All **bench** tests pass; **dummy head** tests meet thresholds; **human** pilot hits: ΔE ≤ **4.0** core, coverage ≥ **95%**, overspray ≤ **1.0%**, no safety violations.
