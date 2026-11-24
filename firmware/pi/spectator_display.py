# hdmi spectator screen layout for maker faire booth

import math
import os
import time
from PIL import Image, ImageDraw, ImageFont


def generate_spectator_screen(output_path: str = "docs/images/ANIMA Spectator Display.png"):
    width, height = 1920, 1080
    img = Image.new("RGB", (width, height), color="#0c1115")
    draw = ImageDraw.Draw(img)

    # Load system fonts with graceful fallbacks
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 40)
        banner_title_font = ImageFont.truetype("arialbd.ttf", 26)
        header_font = ImageFont.truetype("arialbd.ttf", 26)
        hash_font = ImageFont.truetype("consola.ttf", 20)
        label_font = ImageFont.truetype("arial.ttf", 20)
        stat_font = ImageFont.truetype("arialbd.ttf", 54)
        winner_font = ImageFont.truetype("arialbd.ttf", 46)
        score_font = ImageFont.truetype("arialbd.ttf", 80)
        status_font = ImageFont.truetype("arialbd.ttf", 24)
        badge_font = ImageFont.truetype("arialbd.ttf", 20)
    except Exception:
        title_font = banner_title_font = header_font = hash_font = label_font = ImageFont.load_default()
        stat_font = winner_font = score_font = status_font = badge_font = ImageFont.load_default()

    # 1. Top Header Banner
    draw.rectangle([(0, 0), (width, 90)], fill="#141c22")
    draw.line([(0, 90), (width, 90)], fill="#23323d", width=2)
    draw.text((45, 25), "ANIMA : TABLETOP ROCK-PAPER-SCISSORS", fill="#ffffff", font=title_font)

    # Maker Faire Badge
    badge_x = 1480
    draw.rounded_rectangle([(badge_x, 22), (width - 45, 68)], radius=6, fill="#182933", outline="#38a192", width=2)
    draw.text((badge_x + 20, 32), "MAKER FAIRE SHENZHEN 2026", fill="#55d4c2", font=badge_font)

    # 2. SHA-256 Pre-Commitment Banner
    banner_y = 110
    draw.rounded_rectangle([(45, banner_y), (width - 45, banner_y + 105)], radius=10, fill="#162028", outline="#e69519", width=2)
    draw.text((70, banner_y + 16), "FAIR PROTOCOL ACTIVE : MOVE COMMITTED BEFORE COUNTDOWN BEAT 1", fill="#f5a623", font=banner_title_font)
    commitment_hash = "c8129fc8ca43ee3cb5902187d2919abf922718e2098d6f9328a9b23114a87c12"
    draw.text((70, banner_y + 58), f"PRE-COMMITMENT SHA-256 HASH : {commitment_hash}", fill="#ffdb99", font=hash_font)

    # 3. Main Stage: Split into 3 columns
    card_y1, card_y2 = 235, 960

    # ------------------ Column A: Live Camera & Vision Pipeline (Left) ------------------
    col_a_x1, col_a_x2 = 45, 595
    draw.rounded_rectangle([(col_a_x1, card_y1), (col_a_x2, card_y2)], radius=12, fill="#11181f", outline="#202e38", width=2)
    draw.text((col_a_x1 + 30, card_y1 + 25), "CAMERA & VISION PIPELINE", fill="#ffffff", font=header_font)

    # Synthetic camera preview viewport
    cam_box = [(col_a_x1 + 30, card_y1 + 75), (col_a_x2 - 30, card_y1 + 440)]
    draw.rectangle(cam_box, fill="#070b0e", outline="#2a3b47", width=2)

    # Draw grid and targeting reticle
    cx = (cam_box[0][0] + cam_box[1][0]) // 2
    cy = (cam_box[0][1] + cam_box[1][1]) // 2
    draw.ellipse([(cx - 80, cy - 80), (cx + 80, cy + 80)], outline="#26c29d", width=2)
    draw.ellipse([(cx - 40, cy - 40), (cx + 40, cy + 40)], outline="#1e9477", width=1)
    draw.line([(cx - 110, cy), (cx + 110, cy)], fill="#26c29d", width=2)
    draw.line([(cx, cy - 110), (cx, cy + 110)], fill="#26c29d", width=2)
    draw.text((cx, cy + 120), "[ VISITOR PLAYING ZONE ]", fill="#4f7082", font=label_font, anchor="mm")

    # Vision Telemetry details
    t_y = card_y1 + 470
    draw.text((col_a_x1 + 30, t_y), "Physical Shutter Blade :", fill="#9eb0bd", font=label_font)
    draw.text((col_a_x1 + 300, t_y), "OPEN (SNAP 38 ms)", fill="#55d4c2", font=status_font)

    t_y += 55
    draw.text((col_a_x1 + 30, t_y), "Classified Gesture :", fill="#9eb0bd", font=label_font)
    draw.text((col_a_x1 + 300, t_y), "SCISSORS", fill="#ffffff", font=status_font)

    t_y += 55
    draw.text((col_a_x1 + 30, t_y), "Model Confidence :", fill="#9eb0bd", font=label_font)
    draw.text((col_a_x1 + 300, t_y), "94.8%", fill="#f5a623", font=status_font)

    t_y += 55
    draw.text((col_a_x1 + 30, t_y), "Frame Process Time :", fill="#9eb0bd", font=label_font)
    draw.text((col_a_x1 + 300, t_y), "16.4 ms (60 FPS)", fill="#4cd137", font=status_font)

    # ------------------ Column B: Round Matchup & Proof (Center) ------------------
    col_b_x1, col_b_x2 = 625, 1295
    center_b_x = (col_b_x1 + col_b_x2) // 2
    draw.rounded_rectangle([(col_b_x1, card_y1), (col_b_x2, card_y2)], radius=12, fill="#11181f", outline="#202e38", width=2)
    draw.text((center_b_x, card_y1 + 38), "ROUND MATCHUP", fill="#ffffff", font=header_font, anchor="mm")

    # Versus matchup cards
    sub_w = 260
    # Left fighter (ANIMA)
    f_left_cx = col_b_x1 + 160
    draw.text((f_left_cx, card_y1 + 100), "ANIMA THROW", fill="#8ba1b0", font=label_font, anchor="mm")
    draw.text((f_left_cx, card_y1 + 155), "ROCK", fill="#44c9b0", font=stat_font, anchor="mm")

    # Center VS
    draw.text((center_b_x, card_y1 + 155), "VS", fill="#506675", font=header_font, anchor="mm")

    # Right fighter (Visitor)
    f_right_cx = col_b_2_cx = col_b_2_x = col_b_x2 - 160
    draw.text((col_b_2_cx, card_y1 + 100), "VISITOR THROW", fill="#8ba1b0", font=label_font, anchor="mm")
    draw.text((col_b_2_cx, card_y1 + 155), "SCISSORS", fill="#f39c12", font=stat_font, anchor="mm")

    # Winner Banner Box
    win_box = [(col_b_x1 + 35, card_y1 + 235), (col_b_x2 - 35, card_y1 + 365)]
    draw.rounded_rectangle(win_box, radius=10, fill="#133128", outline="#27ae60", width=3)
    draw.text((center_b_x, card_y1 + 300), "ANIMA WINS ROUND!", fill="#2ecc71", font=winner_font, anchor="mm")

    # Cryptographic Proof Reveal Card
    proof_box = [(col_b_x1 + 35, card_y1 + 400), (col_b_x2 - 35, card_y2 - 35)]
    draw.rounded_rectangle(proof_box, radius=10, fill="#0a1014", outline="#1c2b36", width=2)

    draw.text((col_b_x1 + 60, card_y1 + 435), "ROUND PROOF", fill="#f5a623", font=header_font)

    # Verification tick pill
    draw.rounded_rectangle([(col_b_x2 - 245, card_y1 + 422), (col_b_x2 - 60, card_y1 + 458)], radius=6, fill="#1b4624")
    draw.text((col_b_x2 - 152, card_y1 + 440), "VERIFIED FAIR", fill="#4cd137", font=label_font, anchor="mm")

    p_y = card_y1 + 490
    draw.text((col_b_x1 + 60, p_y), "Pre-Committed Move :", fill="#8ba1b0", font=label_font)
    draw.text((col_b_x1 + 300, p_y), "ROCK", fill="#44c9b0", font=label_font)

    p_y += 40
    draw.text((col_b_x1 + 60, p_y), "Secret Nonce :", fill="#8ba1b0", font=label_font)
    draw.text((col_b_x1 + 300, p_y), "9f3e1a0d84bf2760ce41a87b", fill="#ffffff", font=hash_font)

    p_y += 40
    draw.text((col_b_x1 + 60, p_y), "Round UUID :", fill="#8ba1b0", font=label_font)
    draw.text((col_b_x1 + 300, p_y), "e418f2b1-7a6c-4901-b519-74d32e", fill="#ffffff", font=hash_font)

    p_y += 48
    draw.line([(col_b_x1 + 60, p_y), (col_b_x2 - 60, p_y)], fill="#1f303d", width=1)
    p_y += 24
    draw.text((col_b_x1 + 60, p_y), "Formula : SHA-256(ANIMA-RPS-v1 + Round + Move + Nonce)", fill="#8ba1b0", font=hash_font)
    p_y += 32
    draw.text((col_b_x1 + 60, p_y), "Result  : Computed digest strictly matches published hash.", fill="#4cd137", font=hash_font)

    # ------------------ Column C: Telemetry & Scoreboard (Right) ------------------
    col_c_x1, col_c_x2 = 1325, width - 45
    draw.rounded_rectangle([(col_c_x1, card_y1), (col_c_x2, card_y2)], radius=12, fill="#11181f", outline="#202e38", width=2)
    draw.text((col_c_x1 + 30, card_y1 + 25), "EXHIBIT TELEMETRY", fill="#ffffff", font=header_font)

    # Scoreboard
    score_box = [(col_c_x1 + 30, card_y1 + 75), (col_c_x2 - 30, card_y1 + 255)]
    draw.rounded_rectangle(score_box, radius=10, fill="#17222b", outline="#293b47", width=2)

    sc_center_x = (score_box[0][0] + score_box[1][0]) // 2
    draw.text((sc_center_x - 130, card_y1 + 105), "VISITORS", fill="#8ba1b0", font=label_font, anchor="mm")
    draw.text((sc_center_x + 130, card_y1 + 105), "ANIMA", fill="#8ba1b0", font=label_font, anchor="mm")

    draw.text((sc_center_x - 130, card_y1 + 180), "14", fill="#ffffff", font=score_font, anchor="mm")
    draw.text((sc_center_x, card_y1 + 180), "-", fill="#445b6b", font=score_font, anchor="mm")
    draw.text((sc_center_x + 130, card_y1 + 180), "21", fill="#44c9b0", font=score_font, anchor="mm")

    # Actuator & Sensor Grid
    draw.text((col_c_x1 + 30, card_y1 + 295), "Actuator & Sensor Bus (ESP32-S3)", fill="#ffffff", font=header_font)

    sensors = [
        ("Tendon Coil 1 (Index/Middle)", "FIRED (13.8 ms)", "#44c9b0"),
        ("Tendon Coil 2 (Ring/Little)", "REST (0.0 ms)", "#708491"),
        ("Tendon Coil 3 (Thumb)", "REST (0.0 ms)", "#708491"),
        ("Hall Endstop (Index)", "LOCKED CONTACT", "#4cd137"),
        ("Hall Endstop (Middle)", "LOCKED CONTACT", "#4cd137"),
        ("Hall Endstop (Thumb)", "REST CONTACT", "#708491"),
        ("Thermal Bus (Coils)", "32.4 C (NOMINAL)", "#44c9b0"),
        ("Hardware E-Stop Line", "ARMED (HEALTHY)", "#4cd137"),
    ]

    sy = card_y1 + 355
    for name, status, color in sensors:
        draw.text((col_c_x1 + 30, sy), name, fill="#9eb0bd", font=label_font)
        draw.text((col_c_x2 - 30, sy), status, fill=color, font=label_font, anchor="ra")
        sy += 44

    # 4. Footer Bar
    draw.rectangle([(0, height - 60), (width, height)], fill="#141c22")
    draw.line([(0, height - 60), (width, height - 60)], fill="#23323d", width=1)
    draw.text((45, height - 38), "ANIMA ROBOTICS  |  ESP32-S3 UART @ 115200 BAUD  |  MEDIAN THROW LATENCY: 14.1 MS", fill="#6b808e", font=label_font)
    draw.text((width - 45, height - 38), "SYSTEM FPS: 59.8  |  ZERO CHEATING VERIFIED", fill="#2ecc71", font=label_font, anchor="ra")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Generated spectator screen: {output_path}")


if __name__ == "__main__":
    generate_spectator_screen()
