# ANIMA | Fallen submission checklist

This local engineering package is Custom Engineered. Use it to review the rebuilt design and reproduce the checks on the original work you author for Fallen. The program expects the entrant to design and document the submitted work. Add your own README and publish your own sources when complete. The public requirements were checked on 20 November 2026. [Fallen submission guidelines](https://fallen.hackclub.com/docs/submitting)

## Design submission and funding

| Upload or include | What to verify in your rebuild |
| --- | --- |
| Public repository link | In the Fallen project page, check that the title is ANIMA and replace any legacy 51-axis text with your upper-torso design. Open the repo and its attachments in a signed-out browser, submit that link in Design Submission, then confirm receipt in the dashboard. |
| README.md | Write what ANIMA is, how a visitor plays and why you made it. Embed the full assembly, PCB and schematic or wiring screenshots. A studio render is optional. |
| Native CAD including electronics | Use your own `.FCStd`, `.f3d` or shared Onshape document. The package contains CadQuery input, a named STEP assembly and a local FreeCAD import macro. See the verification summary for native export status. Treat imported STEP solids as placement and fit geometry. Build and retain your editable CAD history. |
| Individual STEP | Export every part you modeled. Confirm leaf part names and counts. Include the assembly with Pi, controller, regulators and all actuators visible in CAD. The reference solid generator uses `cadquery==2.6.1` on Python 3.11. |
| KiCad design and fab ZIP | Commit `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, `.kicad_prl`, linked libraries, `gerbers.zip` and the harness diagram. Run ERC, DRC with schematic parity, and view board outline, copper, mask, silkscreen and drill alignment. |
| Firmware and host tools | Include sources, pins, versions, operating commands and test status. Untested firmware is allowed at the design stage. The compiled controller, Pi bench tools and simulated FAIR rehearsal cover part of the live exhibit software. |
| BOM.csv and grant total | Include installed quantities, currency, prices and sourcing links. The monitor and cable are marked owned at ₹0. Replace their reference links with the actual models. `KiCad/PCB_BOM.csv` details 47 grouped assembly rows covered by the ₹4,500 allowance. |

[Fallen submission guidelines](https://fallen.hackclub.com/docs/submitting) · [Fallen project dashboard](https://fallen.hackclub.com/)

- Fallen allocates funding after design approval via an HCB grant card. Request the minimum quantities needed to build the exhibit. Confirm SBC and transport-case eligibility before including them in the grant request. [Fallen funding rules](https://fallen.hackclub.com/docs/project-funding)
- The planning subtotal is **₹58,120.68 for the exhibit** and **₹64,620.68 with the case candidate**, before shipping and outstanding quote changes. Silverline listed the Pi 5 8 GB at ₹16,950 and the ₹5,990 256 GB NVMe kit as out of stock. Resolve SSD availability before you lock the request. The case costs ₹6,500 before GST. Verify fit after padding with the dismantled torso and obtain the final landed quote. [Pi 5 retailer listing](https://www.silverlineelectronics.in/collections/featured-products/products/raspberry-pi-5-model-b-8gb-ram) · [Official SSD kit retailer listing](https://www.silverlineelectronics.in/products/raspberry-pi-official-ssd-kit-iops3-40k-256gb-silverline-electronics-official-distributor) · [Case listing](https://caseandfoam.in/product/ew5620/)
- Confirm the current design cutoff and any account-specific fields in the dashboard. The separate public Shenzhen qualification gate is **an approved working build and 1,000 XP by December 11 at 11:59 PM Eastern Time**. [Fallen Start Here](https://fallen.hackclub.com/docs/start-here)

## Build submission

Submit updated sources and the actual working exhibit. Include photos of the completed robot and a demo video link in your README. Keep journaling your own build progress. A strong demo sequence is a full-body shot, the physical blackout and prior commitment, one uninterrupted live round, the hand pose reveal and the proof check. After power-off, film an independent E-stop test as a separate validation clip. [Fallen submission guidelines](https://fallen.hackclub.com/docs/submitting) · [Fallen Start Here](https://fallen.hackclub.com/docs/start-here)

## ANIMA release gates

1. Can the striker, hand, jaw, eyes and camera shutter complete their full sweeps with guards installed? Check pinch gaps and mounting hardware against real parts. The modeled electronics include provisional purchased-part envelopes.
2. Is the main controller and head harness disabled on E-stop, brownout and unplug? Check power rail decay, fuse behavior and backfeed with total load. Verify cutoff before connecting the mechanism.
3. Does the 12 V / 10 A candidate support all three hot coils during Paper with concurrent motion from the five servos? Record peak and sustained current, minimum rail voltage, coil temperatures, and contact, connector, and PCB temperatures. Lock the exact supply, fuse, wire, connector and copper stackup only after this test.
4. Does the shutter completely cover the sensor in FAIR? Confirm the Hall input and the captured image independently. Display the full hash before the first countdown beat. Abort or fault on an invalid camera frame, uncertain hand classification, missed Hall state or invalid proof. The hash verifies the committed move. Shutter and Hall checks cover the physical round.
5. Complete camera classification, replay, speaker cues, chest animations, and host scheduling. Run repeated rounds under booth lighting, noise and temperature before calling the exhibit operational.
