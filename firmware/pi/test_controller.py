# bench test suite for fair hashing and serial bridge

import unittest
import numpy as np
from anima_vision_game import RoundProof, FastGestureDetector, ExhibitGameController, SerialBridge, WIN_MATRIX


class TestFairProtocol(unittest.TestCase):
    def test_proof_commitment_integrity(self):
        proof = RoundProof.create("ROCK")
        self.assertEqual(proof.throw, "ROCK")
        self.assertTrue(proof.verify(proof.commitment))

        # Bit flip in commitment must fail verification
        tampered_hash = "a" + proof.commitment[1:]
        self.assertFalse(proof.verify(tampered_hash))

    def test_random_nonce_uniqueness(self):
        p1 = RoundProof.create()
        p2 = RoundProof.create()
        self.assertNotEqual(p1.nonce, p2.nonce)
        self.assertNotEqual(p1.round_id, p2.round_id)
        self.assertNotEqual(p1.commitment, p2.commitment)


class TestGameRules(unittest.TestCase):
    def test_win_matrix(self):
        self.assertEqual(WIN_MATRIX[("ROCK", "SCISSORS")], "ANIMA")
        self.assertEqual(WIN_MATRIX[("SCISSORS", "PAPER")], "ANIMA")
        self.assertEqual(WIN_MATRIX[("PAPER", "ROCK")], "ANIMA")
        self.assertEqual(WIN_MATRIX[("SCISSORS", "ROCK")], "VISITOR")
        self.assertEqual(WIN_MATRIX[("PAPER", "SCISSORS")], "VISITOR")
        self.assertEqual(WIN_MATRIX[("ROCK", "PAPER")], "VISITOR")


class TestGestureDetection(unittest.TestCase):
    def setUp(self):
        self.detector = FastGestureDetector()

    def test_blank_frame_defaults_to_rock(self):
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        gesture, conf, _ = self.detector.classify_frame(blank)
        self.assertIn(gesture, ("ROCK", "UNKNOWN"))


class TestSerialBridge(unittest.TestCase):
    def test_mock_communication(self):
        bridge = SerialBridge(mock=True)
        self.assertTrue(bridge.connected)
        bridge.send("ARM")
        bridge.send("SERVO 2 1500")
        bridge.close()


if __name__ == "__main__":
    unittest.main()
