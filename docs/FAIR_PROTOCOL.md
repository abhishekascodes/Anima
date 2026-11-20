# ANIMA FAIR round

1. Latch FAIR mode and close the opaque shutter. Require the shutter Hall input and verify frame blackout during commissioning. Abort the round if closure fails.
2. Create a fresh round ID and randomly chosen move. Generate a 24-byte secret. Publish the round ID and full SHA-256 commitment on the booth HDMI display. Start the countdown after the hash has been shown and keep it visible throughout the round.
3. On the throw cue, command the committed move without using a visitor gesture. Verify the hand pose with the six tendon Hall switches. Treat a failed pose as a foul and release or lock out as appropriate.
4. When the committed pose is verified, show the move and secret. Open the shutter and classify the visitor's held pose. Score only if the gesture and the verified robot pose are both valid.

## Proof format

Hash the ASCII message `ANIMA-RPS-v1\n<round ID>\n<MOVE>\n<secret>\n` with SHA-256. The escape sequences denote actual line breaks. Use lowercase hex for the round ID and secret and `ROCK`, `PAPER` or `SCISSORS` for the move. A spectator who saved the pre-countdown hash can recompute it from the reveal. The shutter and Hall sensors provide the physical evidence of how the round was played.

`Previews/ANIMA Bench Rehearsal.html` implements the visible publication and simulated sensor sequence. `Previews/ANIMA Round Proof.html` demonstrates independent proof checking. `Firmware/pi/anima_show_modules.py commit private.json` prints the public fields and stores the unrevealed fields. `reveal private.json <published-hash>` releases them only when they match the supplied commitment. The live show still needs to connect the Pi display, shutter and Hall events, and camera classifier to this sequence.

## Booth setup

Connect the owned HDMI monitor and cable to the Pi. Position the marked mat and matte backdrop so the camera view contains the visitor's hand against the fixed background. Check crop and contrast under the booth's lighting with the diffuse bar on. Keep START and REMATCH on the physical buttons. The speaker is for playback cues.
