# ANIMA RPS R1 integration notes

This Hardware Release covers the new upper-torso robot. It is Custom Engineered and intended for review and prototyping. Use Fallen's authorship guidelines when deciding what belongs in your own submission. The board is low-voltage DC only.

## Mechanical handoff

Open the assembly STEP to review the 550 mm torso and 420 × 380 mm base. The individual STEP files cover modeled components. The CadQuery script is the editable source and `part_index.json` identifies purchased-part envelopes. Fit, motion stops, guarding, fastener choice and candidate connector geometry need review against purchased hardware. The hand poses in the assembly illustrate the mechanism. Verify loaded travel and coil force with one finger group before cutting the full mechanism. The camera mount starts at 60° down and 26° inward. Confirm the actual crop and opaque shutter coverage before drilling.

## Controller to harness

| Connector | Pin order | Function |
| --- | --- | --- |
| J1 | 1 always-on regulated 5 V, 2 ground | Powers logic, gate drivers and audio amplifier. Use a current-limited supply for first startup. |
| J2 | 1 ground, 2 board RX, 3 board TX | Pi or USB-to-UART adapter at 3.3 V. Cross transmit and receive. No supply wire. |
| J3 | 1 ground, 2 board RX, 3 board TX, 4 EN, 5 BOOT | 3.3 V UART0 programming. Disconnect the Pi UART before using it. |
| J5 | 1 board 3.3 V, 2 healthy-return input | Dry auxiliary contact closes when the external actuator disconnect is healthy. Logic current only. |
| J6 | 1 board 3.3 V, 2 ground, 3 - 8 EXT1, RET1, EXT2, RET2, EXT3, RET3, 9 shutter closed | DRV5033 sensors are active low and board inputs use 10 kΩ pull-ups. Bypass each remote sensor locally and run a ground reference with the signals. |
| J7 - J9 | 1 thermistor sense, 2 ground | One 10 kΩ NTC per coil. Connect the thermistor from sense to ground. The bias resistor and ADC filter are on the board. |
| J10 | 1 ground, 2 FAIR contact, 3 START, 4 REMATCH | Dry contacts to ground. |
| J11 | 1 logic 5 V, 2 ground, 3 board TX to radar RX, 4 board RX from radar TX | Verify the specific LD2410 variant uses compatible 3.3 V UART signaling. |
| J12 - J16 | 1 PWM, 2 signal return | DS3225 head pan, MG996R tilt, DS3225 left elbow, MG90S jaw and MG90S shutter, in order. Feed motor power from the separate switched and fused 6 V loom. |
| J17 | 1 pixel data, 2 ground reference | Pixel 5 V comes from the separate current-limited panel supply. Establish the common DC return at the distribution star. |
| J18 | 1 speaker positive, 2 speaker negative | Floating bridge-tied speaker output. Keep both wires off chassis and signal ground. |
| J19 | 1 switched 12 V, 2 ground | Input downstream of the independent E-stop disconnect. Size the fuse and DC disconnect for the measured simultaneous load. |
| J20 - J22 | 1 coil positive, 2 switched coil return | Index/middle, ring/little and thumb in order. No chassis return at these outputs. |

The independent actuator disconnect removes coil and servo motor power. Maintain logic power for diagnostics. Verify the auxiliary contact and DC branch disconnect separately. Join the coil and servo supply returns at the DC distribution star. Use an enclosed commercial supply, strain relief, and guarded connections. A functional interlock on the PCB does not establish a safety rating for the entire machine.

## Bench order

1. Bring up the board on the 5 V logic supply with actuator feeds removed. Confirm the 3.3 V rail, UART, J5 logic levels and that PWM outputs remain inhibited on reset.
2. Verify connector polarity, gate waveforms, both Hall stops and the cutoff with a current-limited dummy load. Confirm driver bias, gate swing, buck switching and EMI near the Hall loom.
3. Measure the exact coil SKU under load. Check flyback overshoot, initial pull-in, release time, simultaneous Paper rail sag, repeated coil heating and connector and copper temperature. The layout uses 2.0 mm for the 12 V trunk and 1.1 mm for the three switched coil paths. Select board stackup and copper with the measured current and fabricator's limits.
4. Center the servo horns with the mechanism released, then establish travel limits with the actual linkages and guard fitted. Verify shutter blackout and the actual camera frame on the Pi.
5. Exercise the fault cases in the layout and rehearsal, then test the physical exhibit through 100 rounds and a continuous thermal soak.

## ESP32 and Pi bench software

The ESP32 project targets the N8 module using PlatformIO and the Arduino framework. Use a 3.3 V USB-to-UART adapter on J3 for programming. The separate Pi bench console uses pyserial and the controller UART. The bench source covers PWM, gated arm states, pose verification, thermistor checks, bounded retry and a link watchdog. It exposes the physical mode and buttons in status. The HTML rehearsal demonstrates the show flow and publishes a visible FAIR hash with simulated inputs. Camera classification, live replay, playback of voice cues and chest animation still need integration with hardware. START and REMATCH use the fascia buttons.

The controller boots disarmed with no active coil profile. `STATUS` reports contact, shutter, button and Hall states. `PING` refreshes the heartbeat. `PROFILE pull_ms hold_pwm_0_to_255 hold_ms settle_ms temperature_limit_C ntc_beta` sets a volatile, bench-measured profile while disarmed. `ARM` requires recent heartbeats, valid thermistor readings, healthy interlock and all three curl stops. `SERVO index pulse_us` exercises one servo, zero-based in J12 to J16 order. `THROW ROCK`, `THROW SCISSORS` and `THROW PAPER` use the validated profile. `RELEASE` returns the hand to Rock. `STOP` removes enable and latches the controller. `RESET` requires the healthy interlock and curled hand, and leaves the board disarmed.

## Design review

- Open the KiCad project with its included symbol and footprint libraries intact. The ERC and DRC reports specify the verified digital state. Manufacturing exports are review outputs pending electrical and mechanical validation.
- `KiCad/electronic_parts.csv` gives each fitted PCB reference and footprint. `BOM.csv` groups the 47 fitted component lines with the installed hardware and keeps their prices inside the assembly allowance. Verify landed quotes before requesting funds.
- The master brief describes grant eligibility for the Pi and modules as pending. Check the actual organizer reply before procurement.
- [Fallen submission guidelines](https://fallen.hackclub.com/docs/submitting)
- [Espressif schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html)
- [Diodes AP63203 datasheet](https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf)
- [TI UCC27517A gate driver](https://www.ti.com/product/UCC27517A)
- [Infineon IRLZ44N](https://www.infineon.com/part/IRLZ44N)
- [Analog Devices MAX98357A](https://www.analog.com/en/products/max98357a.html)
