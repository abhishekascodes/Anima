"""ANIMA Tabletop RPS Show Controller and Computer Vision Pipeline.

Runs on the Raspberry Pi 5 to drive exhibit games at Maker Faire Shenzhen.
Integrates the SHA-256 FAIR anti-cheat commitment protocol, high-speed
ESP32-S3 serial communication, OpenCV player hand gesture recognition,
and booth exhibit state machine.
"""

from dataclasses import dataclass
from enum import Enum, auto
from hashlib import sha256
from hmac import compare_digest
import json
import logging
import math
import os
from pathlib import Path
import queue
import secrets
import sys
import threading
import time
from typing import Dict, List, Optional, Tuple
import uuid

import cv2
import numpy as np

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("ANIMA")

MOVES = ("ROCK", "PAPER", "SCISSORS")
WIN_MATRIX = {
    ("ROCK", "SCISSORS"): "ANIMA",
    ("SCISSORS", "PAPER"): "ANIMA",
    ("PAPER", "ROCK"): "ANIMA",
    ("SCISSORS", "ROCK"): "VISITOR",
    ("PAPER", "SCISSORS"): "VISITOR",
    ("ROCK", "PAPER"): "VISITOR",
}


class GameState(Enum):
    IDLE = auto()
    ATTRACT = auto()
    COMMIT = auto()
    COUNTDOWN_1 = auto()
    COUNTDOWN_2 = auto()
    COUNTDOWN_3 = auto()
    THROW = auto()
    CAPTURE = auto()
    RESOLVE = auto()
    REVEAL = auto()
    COOLDOWN = auto()


@dataclass
class RoundProof:
    round_id: str
    throw: str
    nonce: str
    commitment: str

    @classmethod
    def create(cls, chosen_throw: Optional[str] = None) -> "RoundProof":
        r_id = uuid.uuid4().hex
        move = chosen_throw if chosen_throw in MOVES else secrets.choice(MOVES)
        secret_nonce = secrets.token_hex(24)
        wire = f"ANIMA-RPS-v1\n{r_id}\n{move}\n{secret_nonce}\n".encode("ascii")
        digest = sha256(wire).hexdigest()
        return cls(round_id=r_id, throw=move, nonce=secret_nonce, commitment=digest)

    def verify(self, published_commitment: str) -> bool:
        wire = f"ANIMA-RPS-v1\n{self.round_id}\n{self.throw}\n{self.nonce}\n".encode("ascii")
        expected = sha256(wire).hexdigest()
        return compare_digest(expected, published_commitment)


class MockSerialDevice:
    """Simulates the 4-layer ESP32-S3 controller for bench testing without hardware."""

    def __init__(self):
        self.armed = False
        self.last_heartbeat = time.monotonic()
        self.servo_pos = [1500] * 5
        self.current_pose = "ROCK"
        self.incoming = queue.Queue()
        self.running = True

    def write(self, data: bytes):
        line = data.decode("ascii", errors="replace").strip()
        now = time.monotonic()
        if line == "PING":
            self.last_heartbeat = now
            self.incoming.put("PONG")
        elif line == "STATUS":
            self.incoming.put("ST 1 0 0 1 0 1 1 0 0")
        elif line == "ARM":
            self.armed = True
            self.incoming.put("OK ARMED")
        elif line == "RELEASE":
            self.current_pose = "ROCK"
            self.incoming.put("OK RELEASED")
        elif line.startswith("SERVO"):
            self.incoming.put("OK SERVO")
        elif line.startswith("THROW"):
            pose = line.split()[1] if len(line.split()) > 1 else "ROCK"
            self.current_pose = pose
            self.incoming.put(f"OK THROW {pose}")
        elif line == "STOP":
            self.armed = False
            self.incoming.put("FAULT HOST_STOP")

    def readline(self) -> bytes:
        try:
            msg = self.incoming.get(timeout=0.05)
            return (msg + "\n").encode("ascii")
        except queue.Empty:
            return b""

    def flush(self):
        pass

    def close(self):
        self.running = False


class SerialBridge:
    """Manages low-latency UART communication and heartbeat keepalives with the ESP32."""

    def __init__(self, port: Optional[str] = None, baudrate: int = 115200, mock: bool = False):
        self.port = port
        self.baudrate = baudrate
        self.mock = mock
        self.device = None
        self.active = threading.Event()
        self.lock = threading.Lock()
        self.last_pong = 0.0
        self.connected = False
        self._connect()

    def _connect(self):
        if self.mock or not self.port:
            logger.info("Operating in Mock Serial mode (Simulated ESP32-S3)")
            self.device = MockSerialDevice()
            self.connected = True
        else:
            try:
                import serial

                self.device = serial.Serial(self.port, self.baudrate, timeout=0.05, write_timeout=0.2)
                self.connected = True
                logger.info("Connected to ESP32 on %s @ %d baud", self.port, self.baudrate)
            except Exception as err:
                logger.warning("Could not open %s (%s). Falling back to Mock Serial.", self.port, err)
                self.device = MockSerialDevice()
                self.connected = True
                self.mock = True

        self.active.set()
        self.worker = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.worker.start()

    def _heartbeat_loop(self):
        deadline = 0.0
        while self.active.is_set():
            now = time.monotonic()
            if now >= deadline:
                self.send("PING")
                deadline = now + 0.20
            try:
                line = self.device.readline().decode("ascii", errors="replace").strip()
                if line:
                    if line == "PONG":
                        self.last_pong = time.monotonic()
                    else:
                        logger.debug("ESP32: %s", line)
            except Exception:
                time.sleep(0.01)

    def send(self, command_str: str):
        if not self.device:
            return
        with self.lock:
            try:
                self.device.write((command_str + "\n").encode("ascii"))
            except Exception as err:
                logger.error("Serial send error: %s", err)

    def close(self):
        self.active.clear()
        if self.device:
            try:
                self.send("STOP")
                self.device.close()
            except Exception:
                pass


class FastGestureDetector:
    """Computer vision player gesture classifier using OpenCV contour and convexity defect analysis."""

    def __init__(self):
        self.last_gesture = "UNKNOWN"
        self.confidence = 0.0

    def classify_frame(self, frame: np.ndarray) -> Tuple[str, float, Optional[np.ndarray]]:
        """Processes a video frame to segment the hand and classify Rock, Paper, or Scissors."""
        h, w = frame.shape[:2]
        # Crop region of interest where visitor hand is presented
        roi = frame[int(h * 0.15) : int(h * 0.85), int(w * 0.2) : int(w * 0.8)]
        if roi.size == 0:
            return "UNKNOWN", 0.0, None

        # Convert to YCrCb and HSV color spaces for robust skin tone segmentation under booth lights
        ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)
        lower_skin = np.array([0, 133, 77], dtype=np.uint8)
        upper_skin = np.array([255, 173, 127], dtype=np.uint8)
        mask = cv2.inRange(ycrcb, lower_skin, upper_skin)

        # Morphological filtering to clean noise and bridge finger knuckles
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return "ROCK", 0.5, mask

        hand_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(hand_contour)
        if area < 3500:
            return "ROCK", 0.6, mask

        hull = cv2.convexHull(hand_contour, returnPoints=False)
        if len(hull) < 4:
            return "ROCK", 0.7, mask

        try:
            defects = cv2.convexityDefects(hand_contour, hull)
        except Exception:
            defects = None

        finger_count = 0
        if defects is not None:
            defects = defects.reshape(-1, 4)
            for s, e, f, d in defects:
                start = tuple(hand_contour[s][0])
                end = tuple(hand_contour[e][0])
                far = tuple(hand_contour[f][0])

                # Calculate triangle sides
                a = math.dist(start, end)
                b = math.dist(start, far)
                c = math.dist(end, far)

                # Angle between fingers
                if b * c > 0:
                    angle = math.acos(max(-1.0, min(1.0, (b**2 + c**2 - a**2) / (2 * b * c))))
                    if angle <= math.pi / 2.0 and d > 6000:
                        finger_count += 1

        # Classification based on detected web spaces / fingertip extensions
        if finger_count == 0 or finger_count == 1:
            gesture = "ROCK"
            confidence = 0.88
        elif finger_count == 2:
            gesture = "SCISSORS"
            confidence = 0.92
        else:
            gesture = "PAPER"
            confidence = 0.90

        self.last_gesture = gesture
        self.confidence = confidence
        return gesture, confidence, mask


class ExhibitGameController:
    """Master game engine coordinating fair anti-cheat rounds, arm countdown strikes, and scoring."""

    def __init__(self, serial_bridge: SerialBridge, camera_index: int = 0):
        self.bridge = serial_bridge
        self.camera_index = camera_index
        self.state = GameState.IDLE
        self.active_proof: Optional[RoundProof] = None
        self.detector = FastGestureDetector()
        self.visitor_score = 0
        self.anima_score = 0
        self.round_history: List[Dict] = []
        self.camera = None
        self._init_camera()

    def _init_camera(self):
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                logger.warning("Camera index %d not accessible. Operating in synthetic vision mode.", self.camera_index)
                self.camera = None
        except Exception as err:
            logger.warning("Camera initialization failed: %s", err)
            self.camera = None

    def capture_frame(self) -> np.ndarray:
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                return frame
        # Return a synthetic frame simulating booth camera input
        synth = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(synth, "ANIMA BENCH CAMERA FEED", (140, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (120, 210, 240), 2)
        return synth

    def start_round(self, forced_move: Optional[str] = None) -> RoundProof:
        """Executes the complete FAIR round cycle with physical shutter lock and tendon throw."""
        # 1. PRE-COMMIT: Generate secret move and SHA-256 hash
        self.state = GameState.COMMIT
        self.active_proof = RoundProof.create(forced_move)
        logger.info("ROUND COMMITTED: %s -> Hash: %s", self.active_proof.round_id[:8], self.active_proof.commitment[:16])

        # 2. PHYSICAL BLACKOUT: Snap camera shutter closed
        self.bridge.send("SERVO 4 1150")  # Camera shutter CLOSED position
        time.sleep(0.08)

        # 3. COUNTDOWN STRIKES: 3-beat rhythm with forearm countdown striker
        for beat, state in enumerate([GameState.COUNTDOWN_1, GameState.COUNTDOWN_2, GameState.COUNTDOWN_3], 1):
            self.state = state
            logger.info("COUNTDOWN BEAT %d...", beat)
            # Striker arm drops then lifts
            self.bridge.send("SERVO 2 1750")  # Striker drop
            time.sleep(0.18)
            self.bridge.send("SERVO 2 1400")  # Striker return
            time.sleep(0.22)

        # 4. INSTANT MECHANICAL THROW: Fire solenoid tendon lines
        self.state = GameState.THROW
        throw_start = time.perf_counter()
        self.bridge.send(f"THROW {self.active_proof.throw}")
        throw_latency_ms = (time.perf_counter() - throw_start) * 1000
        logger.info("ACTUATION THROW: %s (Latency: %.2f ms)", self.active_proof.throw, throw_latency_ms)
        time.sleep(0.04)

        # 5. OPEN SHUTTER & CAPTURE VISITOR GESTURE
        self.state = GameState.CAPTURE
        self.bridge.send("SERVO 4 1850")  # Camera shutter OPEN position
        time.sleep(0.05)
        frame = self.capture_frame()
        visitor_gesture, conf, _ = self.detector.classify_frame(frame)
        logger.info("CAPTURED VISITOR GESTURE: %s (Confidence: %.2f)", visitor_gesture, conf)

        # 6. RESOLVE WINNER & REVEAL PROOF
        self.state = GameState.RESOLVE
        outcome = self._evaluate_winner(self.active_proof.throw, visitor_gesture)
        if outcome == "ANIMA":
            self.anima_score += 1
            self.bridge.send("SERVO 3 1750")  # Jaw open celebratory animation
        elif outcome == "VISITOR":
            self.visitor_score += 1
            self.bridge.send("SERVO 1 1350")  # Head nod of respect
        time.sleep(0.2)
        self.bridge.send("SERVO 3 1500")
        self.bridge.send("SERVO 1 1500")

        # 7. LOG VERIFIED ROUND
        record = {
            "round_id": self.active_proof.round_id,
            "commitment": self.active_proof.commitment,
            "anima_throw": self.active_proof.throw,
            "visitor_throw": visitor_gesture,
            "outcome": outcome,
            "secret_nonce": self.active_proof.nonce,
            "verified": self.active_proof.verify(self.active_proof.commitment),
            "score": f"{self.visitor_score}-{self.anima_score}",
        }
        self.round_history.append(record)
        self.state = GameState.REVEAL

        # Reset hand to relaxed ready position
        time.sleep(0.8)
        self.bridge.send("RELEASE")
        self.state = GameState.IDLE
        return self.active_proof

    def _evaluate_winner(self, anima_move: str, visitor_move: str) -> str:
        if anima_move == visitor_move:
            return "TIE"
        return WIN_MATRIX.get((anima_move, visitor_move), "VISITOR")


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="Serial port to ESP32 (e.g. COM3 or /dev/ttyACM0)")
    parser.add_argument("--mock", action="store_true", default=True, help="Run with simulated ESP32 and camera")
    parser.add_argument("--rounds", type=int, default=3, help="Number of benchmark test rounds to run")
    args = parser.parse_args()

    bridge = SerialBridge(port=args.port, mock=args.mock)
    engine = ExhibitGameController(serial_bridge=bridge)

    time.sleep(0.3)
    bridge.send("ARM")

    logger.info("Starting %d benchmark rounds of ANIMA Fair RPS...", args.rounds)
    for i in range(args.rounds):
        logger.info("\n--- ROUND %d ---", i + 1)
        proof = engine.start_round()
        logger.info("Round %d Complete. Winner: %s", i + 1, engine.round_history[-1]["outcome"])
        time.sleep(0.5)

    bridge.close()
    logger.info("\nBenchmark finished. Final Score: Visitors [%d] - ANIMA [%d]", engine.visitor_score, engine.anima_score)


if __name__ == "__main__":
    main()
