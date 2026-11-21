# ANIMA: Interactive Tabletop Rock-Paper-Scissors Robot

Hey! I am Abhishek, and this is **ANIMA**, an interactive humanoid tabletop robot designed to play Rock-Paper-Scissors with people in real time. I am building this project for **Hack Club Fallen** with the goal of bringing it to showcase at **Maker Faire Shenzhen 2026**.

![ANIMA Robot Showcase](docs/images/ANIMA%20Studio%20Assembly.png)

---

## The Backstory (Or how I almost built an uncontrollable monster)

When I first started this project, I went down a crazy rabbit hole trying to build a 51-axis radial sphere organism. I thought having 48 micro servos wiggling in a giant ball would look incredible. 

It did not. 

Once I actually modeled it and ran the mechanical load numbers, reality hit me pretty hard:
1. **The power draw was absurd:** 48 servos running under load would pull upwards of 50 to 60 amps at stall. Trying to route that through moving joints is an easy way to start an electrical fire on a table.
2. **The physics did not work:** The moment arms on the radial links put massive cantilever bending torque right onto tiny plastic servo splines. They would have stripped in ten minutes.
3. **It was not fun to interact with:** At the end of the day, it was just a mechanical ball wiggling on a pole. People at a booth would look at it for five seconds and walk away.

So I scrapped the entire thing and pivoted to something I actually care about: a robot with personality that people can walk up to, play against, and laugh with. That is where ANIMA was born.

---

## Why Rock-Paper-Scissors? (And the Anti-Cheat Problem)

Almost every Rock-Paper-Scissors robot you see on YouTube or in research labs has a dirty secret: **it cheats**. 

They mount a 120 FPS high-speed camera pointed at your hand, run a lightweight computer vision model that detects the first 20 milliseconds of your fingers unfolding, and snap their winning move right before you finish throwing. You feel like the robot has superhuman reflexes, but really it is just waiting for you to commit and picking the counter.

I wanted ANIMA to play like a real human, with genuine stakes and proof that it is not looking at your hand:

* **Pre-Commitment:** Before the countdown even starts, the host computer picks its move randomly, hashes it with a 24-byte secret key using SHA-256, and splashes the hash across the big screen.
* **Physical Blackout:** While the countdown is running, a micro servo swings a physical, opaque blackout shutter blade over the camera lens. The robot literally cannot see you.
* **Instant Mechanical Throw:** On the final beat, high-speed electromagnetic solenoids yank Kevlar tendons to snap the fingers into Rock, Paper, or Scissors in under 15 milliseconds.
* **Cryptographic Reveal:** Digital Hall effect sensors at the finger stops verify that the hand physically reached the pose. Only after the physical throw is locked does the camera shutter swing open, the secret key get published, and the winner get called. Anyone watching can verify the hash matches the pre-countdown commitment.

---

## Visual Showcase

| Hero Striker Angle | Expressive Portrait View |
| :---: | :---: |
| ![ANIMA Striker Angle](docs/images/ANIMA%20Studio%20Striker%20Side.png) | ![ANIMA Portrait](docs/images/ANIMA%20Studio%20Portrait.png) |

| Internal Cutaway & Tendon Routing | High-Speed Playing Hand |
| :---: | :---: |
| ![ANIMA Cutaway](docs/images/ANIMA%20RPS%20Electronics%20Cutaway.png) | ![ANIMA Playing Hand](docs/images/ANIMA%20Studio%20Hand.png) |

| Custom 4-Layer Controller (KiCad 10) | Multi-Sheet Schematic |
| :---: | :---: |
| ![ANIMA Controller PCB](docs/images/ANIMA%20RPS%20PCB.png) | ![ANIMA Schematic](docs/images/ANIMA%20RPS%20Schematic.png) |

---

## How It Works Under the Hood

### 1. Mechanics and 3D Printed Parts
I split the 3D design into two layers:
* **The structural skeleton (`cad/Parts/` and `ANIMA_RPS_Upper_Torso.FCStd`):** Modeled with exact engineering tolerances in FreeCAD and CadQuery. Every joint that experiences side loads (like the neck pan and striker arm) rides on 688ZZ radial ball bearings so the motor shafts never take bending stress. Brass M3 heat-set inserts are melted into every mounting boss so you can disassemble and rebuild it without stripping plastic threads.
* **The sculpted outer shell (`cad/ANIMA Studio.blend` and `.glb`):** Modeled in Blender to give ANIMA a friendly, retro-futuristic aesthetic. The outer shells cover all the ugly wire harnesses while leaving airflow ducts for the heatsinks and solenoids.

For the fingers, standard servos were way too slow (they take 100 to 200 ms to rotate 60 degrees). Instead, I used **12V pull solenoids** attached to braided 100 lb Dyneema/Kevlar lines running through low-friction PTFE guide tubes. When a coil fires, the fingers snap shut in about 12 to 15 ms, fast enough to match human reflex speed.

### 2. Custom 4-Layer PCB (`ANIMA_RPS_Controller`)
You cannot run high-current inductive solenoids off breadboards or standard hobby shields without crashing your microcontroller. Every time a solenoid coil turns off, the collapsing magnetic field throws a massive negative voltage spike that resets the CPU.

To solve this, I designed a dedicated 4-layer PCB in KiCad 10:
* **Brain:** ESP32-S3-WROOM-1 module running hardware PWM timers and fast GPIO pin-change interrupts for the Hall effect limit sensors.
* **Power Isolation:** The 3.3V digital logic has its own ground plane and is powered through an onboard AP63203 buck converter. The 12V coil rail is completely separated, driven by fast UCC27517 gate drivers, IRLZ44N power MOSFETs, SS54 Schottky catch diodes, and SMBJ24A TVS diodes to soak up inductive kickback.
* **Safety Hardware:** A physical emergency stop button runs straight into an onboard SN74LVC1G00 hardware logic gate. If someone hits the E-stop, the power to all coils and servos is killed in hardware immediately, even if the microcontroller firmware locks up.
* **Audio & Presence:** An onboard MAX98357A I2S Class-D amplifier drives an internal speaker for voice lines and sound effects, and an LD2410 24 GHz mmWave radar header detects when someone walks up to the booth.

### 3. Firmware and Software Architecture
* **ESP32-S3 Firmware (`firmware/esp32/`):** Written in C++ using PlatformIO. Uses high-resolution hardware timers (LEDC) to command servos with zero jitter. When a move is triggered, it pulses the solenoid MOSFETs with an initial 100% kick for 25 ms to overcome mechanical inertia, then drops to a 30% PWM hold current so the coils do not overheat.
* **Host Vision & Game Engine (`firmware/pi/`):** Runs on a Raspberry Pi 5. It handles MediaPipe hand tracking for visitor gesture recognition, manages game state, drives the HDMI commitment display, and communicates with the ESP32 over high-speed USB-serial at 921,600 baud.

---

## Repository Tour

Here is what you will find in this repo:

```
├── cad/
│   ├── README.md                     # Joint angles, mechanical specs and print settings
│   ├── ANIMA Studio.blend            # Master Blender model for outer shells and renders
│   ├── ANIMA Studio.glb              # 3D web asset you can view in your browser
│   ├── ANIMA Studio Fairing Envelopes.step # Clean exterior CAD surfaces
│   ├── ANIMA_RPS_Upper_Torso.FCStd   # Parametric FreeCAD assembly
│   ├── ANIMA_RPS_Upper_Torso.step    # Full structural assembly STEP
│   ├── anima_rps_assembly.py         # Python CadQuery script generating the skeleton
│   └── Parts/                        # All 41 individual 3D printable leaf parts
├── electronics/
│   ├── ANIMA_RPS_Controller.kicad_sch # Complete 8-sheet KiCad schematic (0 ERC errors)
│   ├── ANIMA_RPS_Controller.kicad_pcb # Routed 4-layer PCB layout (0 DRC errors)
│   ├── gerbers.zip                   # Ready-to-order fab package for JLCPCB / PCBWay
│   └── PCB_BOM.csv                   # Part numbers and footprints for all 47 components
├── firmware/
│   ├── esp32/                        # PlatformIO C++ firmware with hardware timers
│   └── pi/                           # Python host scripts and FAIR anti-cheat demo
├── docs/
│   ├── FAIR_PROTOCOL.md              # Deep dive into the SHA-256 anti-cheat protocol
│   ├── INTEGRATION.md                # Wiring harnesses, connectors and pinouts
│   └── images/                       # PCB renders, CAD cutaways and showcase shots
├── bom.csv                           # Full itemized grant BOM in USD ($757.20)
└── README.md
```

---

## Current Status & Next Steps

* [x] Complete mechanical overhaul from radial monster to tabletop humanoid
* [x] Design 41 structural parts in FreeCAD with 688ZZ bearing supports
* [x] Sculpt exterior aesthetic shells in Blender and export STEP envelopes
* [x] Design custom 4-layer PCB in KiCad 10 (ERC: 0 errors, DRC: 0 errors)
* [x] Generate production Gerbers and fitted component BOM
* [x] Write ESP32-S3 firmware with solenoid kick/hold logic
* [x] Write Python FAIR protocol benchmark and camera shutter lock script
* [ ] 3D print structural frame in PETG (0.2mm layer height, 4 walls)
* [ ] Order custom PCB and solder surface mount parts
* [ ] Assemble tendon hand and bench-test 15ms reaction times
* [ ] Pack it all up and take it to Shenzhen!

---

Built with a lot of coffee and late nights by Abhishek A S for Hack Club Fallen.
