# ANIMA CAD & Mechanical Engineering

This directory contains the complete mechanical design, kinematics, and 3D printable files for the **ANIMA Tabletop Rock-Paper-Scissors Robot**.

---

## 3D Model Architecture

ANIMA combines parametric mechanical engineering with ergonomic exterior fairings:

1. **Parametric Engineering CAD (`anima_rps_assembly.py` & `ANIMA_RPS_Upper_Torso.FCStd`):**
   - Built in CadQuery and native FreeCAD.
   - Defines strict mechanical tolerances, internal bearing seats (688ZZ), tendon routing channels, PCB mounting standoffs, and Hall effect sensor pockets.
   - Outputs the 41 custom modeled leaf parts in `Parts/`.

2. **Sculpted Studio Model (`ANIMA Studio.blend`, `.glb`, & `.step`):**
   - Master Blender file containing the high-poly humanoid fairings, neck bellows gaiter, shoulder shells, and visor geometry.
   - Interactive 3D asset (`ANIMA Studio.glb`) for real-time web inspection.
   - Production exterior shell envelopes (`ANIMA Studio Fairing Envelopes.step`).

---

## Degrees of Freedom & Kinematics

| Joint / Actuator | Mechanism | Motor / Actuator | Range of Motion | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Neck Pan** | Direct drive + 688ZZ bearing | MG996R (11 kg-cm) | 180° horizontal sweep | Visitor tracking |
| **Neck Tilt** | Hinge pivot + dual cheek brackets | MG996R (11 kg-cm) | +25° / -15° vertical pitch | Gaze alignment |
| **Jaw Articulation** | Cam linkage | MG90S micro servo | 35° opening | Speech audio sync |
| **Right Forearm Pitch** | 4-bar linkage striker | DS3225 (25 kg-cm) | 90° rapid drop | Countdown strikes |
| **Camera Shutter** | Rotary blackout blade | MG90S micro servo | 60° snap | Anti-cheat physical blackout |
| **Fingers (Index + Middle)** | Kevlar tendon + return spring | JF-0730B pull solenoid (12V) | 14 mm stroke (<15 ms) | Scissors / Paper gesture |
| **Fingers (Ring + Little)** | Kevlar tendon + return spring | JF-0730B pull solenoid (12V) | 14 mm stroke (<15 ms) | Paper gesture |
| **Thumb** | Kevlar tendon + return spring | JF-0730B pull solenoid (12V) | 12 mm stroke (<15 ms) | Rock / Paper gesture |

---

## 3D Printing & Fabrication Guide

* **Recommended Material:** PETG or ABS for thermal stability around motor and solenoid brackets; PLA acceptable for non-load bearing exterior cosmetic shells.
* **Slicer Settings:**
  * 0.20 mm layer height (0.4 mm nozzle)
  * 4 perimeter walls for structural rigidity
  * 25% gyroid infill
* **Hardware & Fasteners:**
  * All structural pivots use standard M3 stainless socket head screws.
  * Hinge points use 688ZZ radial ball bearings (8 mm OD, 3 mm ID, 4 mm thickness) so motor splines experience zero radial shear force.
  * M3x4x5 brass heat-set inserts on all frame connections.
  * Braided Dyneema line (0.8 mm, 100 lb test) for low-friction finger tendon routing through PTFE guide sleeves.
