#ifndef CONFIG_H
#define CONFIG_H

// Channel Configuration
#define TOTAL_CHANNELS 51
#define NUM_PCA9685 4
#define NUM_INA219 6

// I2C Bus 0 Pins (PCA9685 PWM Drivers)
#define I2C0_SDA_PIN 8
#define I2C0_SCL_PIN 9

// I2C Bus 1 Pins (INA219 Current Telemetry)
#define I2C1_SDA_PIN 17
#define I2C1_SCL_PIN 18

// PCA9685 I2C Base Addresses
#define PCA9685_ADDR_0 0x40
#define PCA9685_ADDR_1 0x41
#define PCA9685_ADDR_2 0x42
#define PCA9685_ADDR_3 0x43

// INA219 I2C Base Addresses (6 Banks, 4 Limbs per Bank)
#define INA219_ADDR_0 0x40
#define INA219_ADDR_1 0x41
#define INA219_ADDR_2 0x44
#define INA219_ADDR_3 0x45
#define INA219_ADDR_4 0x46
#define INA219_ADDR_5 0x47

// I2S Audio Interface Pins (INMP441 Mic & MAX98357A Amp)
#define I2S_BCLK_PIN 4
#define I2S_LRC_PIN  5
#define I2S_DIN_PIN  6  // From INMP441 Microphone SD
#define I2S_DOUT_PIN 7  // To MAX98357A Amplifier DIN

// Motion & Safety Parameters
#define STEP_SPEED 2            // Max degrees per 10ms loop step (limits jerk and inrush current)
#define MAX_BANK_CURRENT_MA 4500.0f  // 4.5A current limit per 4-limb bank
#define WATCHDOG_TIMEOUT_MS 3000     // 3 seconds communication watchdog

#endif // CONFIG_H
