# ANIMA: Tabletop Rock-Paper-Scissors Robot

An interactive, tabletop humanoid upper torso robot built for **Hack Club Fallen** and showcasing at **Maker Faire Shenzhen 2026**.

Designed and built by Abhishek A S.

---

## What is ANIMA?

Honestly, I spent the first 6 hours of this build trying to make an insane 51-axis radial bio-organism. But once I rendered the 3D model, it looked like a rigid, awkward spider ball. Worse, the mechanical load math showed that standard servo splines would shear off under radial cantilever weight, and trying to route 60 amps of power across 24 moving limbs was asking for a fire.

So I scrapped it and pivoted hard: **ANIMA is now a high-speed, interactive tabletop Rock-Paper-Scissors (RPS) torso.**

Instead of just wiggling motors on a stand, ANIMA actually plays against visitors at the booth in real time. It uses a combination of high-torque servos for expressive head/arm motion, electromagnetic tendon coils for finger throws, and a cryptographic anti-cheat commitment protocol so visitors know the robot isn't reading their hand late.

---

## Project Showcase

| Tabletop Torso Assembly (420 x 380 x 550 mm) | Internal Cutaway & Tendon Routing |
| :---: | :---: |
| ![ANIMA Torso Assembly](docs/images/ANIMA%20RPS%20Assembly.png) | ![ANIMA Cutaway](docs/images/ANIMA%20RPS%20Electronics%20Cutaway.png) |

| Custom 4-Layer Controller (KiCad 10) | Multi-Sheet Schematic |
| :---: | :---: |
| ![ANIMA Controller PCB](docs/images/ANIMA%20RPS%20PCB.png) | ![ANIMA Schematic](docs/images/ANIMA%20RPS%20Schematic.png) |

---

## How It Works

### 1. Hybrid Actuation
- **5 Servos:** Neck pan, neck tilt, elbow pitch, jaw articulation (syncing to audio lines), and an internal high-speed camera shutter. All servo shafts are supported by 688ZZ radial bearings so the horns never take direct side loads.
- **3 Electromagnetic Tendon Coils:** High-speed solenoids pulling braided Kevlar lines for the hand gestures:
  - Channel 1: Index + Middle fingers
  - Channel 2: Ring + Little fingers
  - Channel 3: Thumb
- **7 Hall Effect Sensors:** DRV5033 digital Hall sensors placed at stroke limits (extension and retraction) to physically confirm finger posture in under 15 milliseconds.

### 2. The FAIR Anti-Cheat Protocol
In most RPS robots, the machine cheats by using a high-speed camera to classify your gesture at 60 fps and throwing its move a fraction of a second later. ANIMA physically proves it plays fair:
1. **Pre-Commitment:** Before countdown beat 1, the host computer generates a random move and a 24-byte secret key, computes a SHA-256 hash, and displays the hash full-screen on an external HDMI monitor.
2. **Physical Blackout:** An opaque mechanical shutter blade physically covers the camera sensor during the entire countdown.
3. **Mechanical Verification:** On the throw cue, the tendon coils fire. The 6 finger Hall sensors verify that the hand actually reached the committed physical pose.
4. **Reveal & Proof:** Once the Hall sensors confirm the mechanical throw, the shutter snaps open, the secret key is published on the screen, and spectators can verify the SHA-256 hash matches the pre-countdown commitment.

---

## Custom Electronics (KiCad 10)

The entire robot runs on a custom 4-layer PCB (`ANIMA_RPS_Controller`):
- **MCU:** ESP32-S3-WROOM-1-N8 running low-jitter LEDC hardware timers for PWM and GPIO interrupts for the Hall stops.
- **Power Architecture:** Dual-rail design with strict power isolation:
  - 5V logic input stepped down to 3.3V 2A via an onboard AP63203 synchronous buck converter.
  - Fused 12V / 10A rail for the inductive finger coils, isolated with UCC27517 high-speed gate drivers, IRLZ44N power MOSFETs, SS54 Schottky clamp diodes, and SMBJ24A transient suppressors.
- **Hardware E-Stop:** An SN74LVC1G00 hardware logic gate wired directly to an external maintained emergency stop button. If the E-stop is hit or software crashes, coil and servo PWM are disabled in hardware.
- **Audio & Presence:** Onboard MAX98357A I2S Class-D amplifier driving a booth speaker, plus an LD2410 24 GHz mmWave radar header for visitor tracking.

---

## Repository Structure

```
├── cad/
│   ├── ANIMA_RPS_Upper_Torso.FCStd   # Native FreeCAD master assembly
│   ├── ANIMA_RPS_Upper_Torso.step    # Full CAD assembly STEP
│   ├── anima_rps_assembly.py         # Parametric CadQuery assembly script
│   └── Parts/                        # 41 individual modeled leaf part STEP files
├── electronics/
│   ├── ANIMA_RPS_Controller.kicad_sch # 8-block KiCad schematic (0 ERC errors)
│   ├── ANIMA_RPS_Controller.kicad_pcb # 4-layer routed board (0 DRC errors)
│   ├── gerbers.zip                   # Complete 13-file manufacturing fab package
│   └── PCB_BOM.csv                   # 47 fitted board components
├── firmware/
│   ├── esp32/                        # PlatformIO C++ firmware with hardware timers
│   └── pi/                           # Python host scripts and FAIR protocol tools
├── docs/
│   ├── FAIR_PROTOCOL.md              # Anti-cheat proof specification
│   ├── INTEGRATION.md                # System integration and harness guide
│   └── images/                       # Renders and schematics
├── bom.csv                           # Full 94-line exhibit BOM (₹58,120.68)
└── README.md
```

---

## Verification & Status

- **CAD Envelope:** Checked at 420 x 380 x 550 mm with 41 unique modeled parts.
- **KiCad ERC:** 0 violations, 0 warnings.
- **KiCad DRC:** 0 violations, 0 unconnected items.
- **Firmware:** Compiled cleanly under PlatformIO for ESP32-S3.
- **Gerbers:** 13 fabrication layers ready for JLCPCB / PCBWay manufacturing.
