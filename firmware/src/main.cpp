#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <Adafruit_INA219.h>
#include <driver/i2s.h>
#include "config.h"

// 4x PCA9685 PWM Drivers on I2C Bus 0 (Wire)
Adafruit_PWMServoDriver pwmDrivers[NUM_PCA9685] = {
    Adafruit_PWMServoDriver(PCA9685_ADDR_0, Wire),
    Adafruit_PWMServoDriver(PCA9685_ADDR_1, Wire),
    Adafruit_PWMServoDriver(PCA9685_ADDR_2, Wire),
    Adafruit_PWMServoDriver(PCA9685_ADDR_3, Wire)
};

// 6x INA219 Current Monitors on I2C Bus 1 (Wire1)
Adafruit_INA219 currentSensors[NUM_INA219] = {
    Adafruit_INA219(INA219_ADDR_0),
    Adafruit_INA219(INA219_ADDR_1),
    Adafruit_INA219(INA219_ADDR_2),
    Adafruit_INA219(INA219_ADDR_3),
    Adafruit_INA219(INA219_ADDR_4),
    Adafruit_INA219(INA219_ADDR_5)
};

// Target and current servo pulse widths (microseconds)
uint16_t currentPositions[TOTAL_CHANNELS];
uint16_t targetPositions[TOTAL_CHANNELS];

unsigned long lastCommandTime = 0;
bool safetyTripped = false;

// Convert degrees (0-180) to PCA9685 12-bit tick count (at 50Hz, 1 tick ~ 4.88us)
uint16_t angleToTicks(float degrees, uint16_t minUs, uint16_t maxUs) {
    degrees = constrain(degrees, 0.0f, 180.0f);
    float us = minUs + (degrees / 180.0f) * (maxUs - minUs);
    return (uint16_t)((us / 20000.0f) * 4096.0f);
}

void initI2S() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_TX),
        .sample_rate = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 256,
        .use_apll = false
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_BCLK_PIN,
        .ws_io_num = I2S_LRC_PIN,
        .data_out_num = I2S_DOUT_PIN,
        .data_in_num = I2S_DIN_PIN
    };

    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pin_config);
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("[ANIMA] 51-Axis Bio-Robotic Organism Initializing...");

    // Initialize I2C Bus 0 for PCA9685 PWM Drivers
    Wire.begin(I2C0_SDA_PIN, I2C0_SCL_PIN, 400000);
    for (int i = 0; i < NUM_PCA9685; i++) {
        pwmDrivers[i].begin();
        pwmDrivers[i].setOscillatorFrequency(27000000);
        pwmDrivers[i].setPWMFreq(50); // 50 Hz standard analog/digital servo frequency
    }

    // Initialize I2C Bus 1 for INA219 Current Telemetry
    Wire1.begin(I2C1_SDA_PIN, I2C1_SCL_PIN, 400000);
    for (int i = 0; i < NUM_INA219; i++) {
        if (!currentSensors[i].begin(&Wire1)) {
            Serial.printf("[WARN] INA219 at bank %d not responding\n", i);
        }
    }

    // Initialize I2S Audio Pipeline
    initI2S();

    // Default neutral home positions (90 degrees across all 51 axes)
    for (int i = 0; i < TOTAL_CHANNELS; i++) {
        targetPositions[i] = 90;
        currentPositions[i] = 90;
    }

    lastCommandTime = millis();
    Serial.println("[ANIMA] Hardware initialization complete. System online.");
}

void checkCurrentLimits() {
    float totalCurrent_mA = 0;
    for (int i = 0; i < NUM_INA219; i++) {
        float current_mA = currentSensors[i].getCurrent_mA();
        totalCurrent_mA += current_mA;
        if (current_mA > MAX_BANK_CURRENT_MA) {
            Serial.printf("[FAULT] Overcurrent detected on Bank %d: %.1f mA\n", i, current_mA);
            safetyTripped = true;
        }
    }

    if (safetyTripped) {
        // Disable PWM outputs across all chips to protect servos and power supply
        for (int i = 0; i < NUM_PCA9685; i++) {
            for (int ch = 0; ch < 16; ch++) {
                pwmDrivers[i].setPWM(ch, 0, 4096); // Full OFF
            }
        }
        Serial.println("[FAULT] Emergency stop engaged. All actuators halted.");
    }
}

void loop() {
    // 1. Process Serial Commands from Host (Vision/IK pipeline)
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        if (cmd.startsWith("SET")) {
            // Format: SET <channel> <angle>
            int ch = -1;
            float angle = 0;
            int parsed = sscanf(cmd.c_str(), "SET %d %f", &ch, &angle);
            if (parsed == 2 && ch >= 0 && ch < TOTAL_CHANNELS) {
                targetPositions[ch] = (uint16_t)angle;
                lastCommandTime = millis();
            }
        } else if (cmd == "HOME") {
            for (int i = 0; i < TOTAL_CHANNELS; i++) targetPositions[i] = 90;
            lastCommandTime = millis();
        } else if (cmd == "RESET_ESTOP") {
            safetyTripped = false;
            Serial.println("[INFO] Safety reset acknowledged.");
        }
    }

    // 2. Watchdog: check for communication loss
    if (millis() - lastCommandTime > WATCHDOG_TIMEOUT_MS && !safetyTripped) {
        // Smoothly return to safe rest pose
        for (int i = 0; i < TOTAL_CHANNELS; i++) targetPositions[i] = 90;
    }

    // 3. Smooth S-Curve / Linear Interpolation toward target positions
    if (!safetyTripped) {
        for (int i = 0; i < TOTAL_CHANNELS; i++) {
            if (currentPositions[i] < targetPositions[i]) {
                currentPositions[i] = min((uint16_t)(currentPositions[i] + STEP_SPEED), targetPositions[i]);
            } else if (currentPositions[i] > targetPositions[i]) {
                currentPositions[i] = max((uint16_t)(currentPositions[i] - STEP_SPEED), targetPositions[i]);
            }

            int driverIdx = i / 16;
            int channelIdx = i % 16;
            if (driverIdx < NUM_PCA9685) {
                uint16_t ticks = angleToTicks(currentPositions[i], 500, 2500);
                pwmDrivers[driverIdx].setPWM(channelIdx, 0, ticks);
            }
        }
    }

    // 4. Sample Current Telemetry (every 100ms)
    static unsigned long lastTelemetry = 0;
    if (millis() - lastTelemetry > 100) {
        lastTelemetry = millis();
        checkCurrentLimits();
    }

    delay(10);
}
