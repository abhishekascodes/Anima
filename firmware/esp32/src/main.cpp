#include <Arduino.h>
#include <driver/mcpwm.h>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <initializer_list>

namespace {
constexpr uint8_t coilPins[] = {4, 5, 6};
constexpr uint8_t hallExt[] = {10, 12, 14};
constexpr uint8_t hallRet[] = {11, 13, 21};
constexpr uint8_t thermPins[] = {9, 8, 1};
constexpr uint8_t servoPins[] = {7, 15, 16, 17, 18};
constexpr uint8_t shutterHall = 2;
constexpr uint8_t stopHealthy = 19;
constexpr uint8_t armOutput = 38;
constexpr uint8_t modeInput = 35;
constexpr uint8_t startInput = 36;
constexpr uint8_t rematchInput = 37;
constexpr uint32_t heartbeatWindow = 750;
constexpr uint32_t stableTime = 12;
constexpr uint32_t curlWindow = 350;

struct Profile {
  unsigned pullMs = 0, holdDuty = 0, holdMs = 0, settleMs = 0, limitC = 0, beta = 0;
};
Profile profile;
enum class Motion { Idle, Pull, Hold, Curl };
Motion motion = Motion::Idle;
bool armed = false, faulted = false, retryAfterCurl = false;
uint8_t targetMask = 0, attempt = 0;
uint32_t lastHeartbeat = 0, motionStart = 0, stableStart = 0, lastThermal = 0;
bool stableActive = false;
char input[90];
size_t inputLen = 0;
bool overflow = false;

void status(const char* text) { Serial.println(text); }

void writeCoils(uint8_t mask, unsigned duty) {
  for (uint8_t i = 0; i < 3; ++i) ledcWrite(i, (mask & (1 << i)) ? duty : 0);
}

bool contactOkay() { return digitalRead(stopHealthy) == HIGH; }

bool matches(uint8_t mask) {
  for (uint8_t i = 0; i < 3; ++i) {
    const bool ext = digitalRead(hallExt[i]) == LOW;
    const bool ret = digitalRead(hallRet[i]) == LOW;
    const bool expected = (mask & (1 << i)) != 0;
    if (ext != expected || ret == expected) return false;
  }
  return true;
}

bool stable(uint8_t mask, uint32_t time) {
  if (!matches(mask)) {
    stableActive = false;
    return false;
  }
  if (!stableActive) {
    stableActive = true;
    stableStart = time;
  }
  return time - stableStart >= stableTime;
}

void cut(const char* reason, bool latch) {
  digitalWrite(armOutput, LOW);
  writeCoils(0, 0);
  armed = false;
  faulted = faulted || latch;
  motion = Motion::Idle;
  retryAfterCurl = false;
  status(reason);
}

bool thermalOkay() {
  for (const uint8_t pin : thermPins) {
    const double mv = analogReadMilliVolts(pin);
    if (mv < 60.0 || mv > 3190.0 || profile.beta == 0) return false;
    const double resistance = 10000.0 * mv / (3300.0 - mv);
    const double kelvin = 1.0 / (1.0 / 298.15 + std::log(resistance / 10000.0) / profile.beta);
    if (!std::isfinite(kelvin) || kelvin - 273.15 >= profile.limitC) return false;
  }
  return true;
}

void beginThrow(uint32_t time) {
  ++attempt;
  motion = Motion::Pull;
  motionStart = time;
  stableActive = false;
  writeCoils(targetMask, 255);
  status("EV THROW");
}

void curl(uint32_t time, bool retry) {
  writeCoils(0, 0);
  motion = Motion::Curl;
  motionStart = time;
  stableActive = false;
  retryAfterCurl = retry;
}

void serviceMotion(uint32_t time) {
  const uint32_t age = time - motionStart;
  switch (motion) {
    case Motion::Idle: return;
    case Motion::Pull: {
      const bool seated = stable(targetMask, time);
      if (age >= profile.pullMs) writeCoils(targetMask, profile.holdDuty);
      if (seated && age <= profile.settleMs) {
        // Never hold at full current past the configured pulse deadline.
        writeCoils(targetMask, profile.holdDuty);
        motion = Motion::Hold;
        motionStart = time;
        status("EV LOCKED");
      } else if (age >= profile.settleMs) {
        status("EV FOUL");
        if (attempt == 1) curl(time, true);
        else cut("FAULT POSE", true);
      }
      return;
    }
    case Motion::Hold:
      if (!matches(targetMask)) cut("FAULT LOST_POSE", true);
      else if (age >= profile.holdMs) curl(time, false);
      return;
    case Motion::Curl:
      if (stable(0, time)) {
        status("EV CURLED");
        if (retryAfterCurl) beginThrow(time);
        else motion = Motion::Idle;
      } else if (age >= curlWindow) cut("FAULT RETURN", true);
      return;
  }
}

void setServo(unsigned index, unsigned usec) {
  const auto timer = static_cast<mcpwm_timer_t>(index / 2);
  const auto signal = index % 2 == 0 ? MCPWM_OPR_A : MCPWM_OPR_B;
  mcpwm_set_duty_in_us(MCPWM_UNIT_0, timer, signal, usec);
  mcpwm_set_duty_type(MCPWM_UNIT_0, timer, signal, MCPWM_DUTY_MODE_0);
}

void stateReport() {
  Serial.printf("STATUS ARM=%u FAULT=%u AUX=%u SHUT=%u MODE=%s START=%u REMATCH=%u EXT=%u%u%u RET=%u%u%u\n",
    armed, faulted, contactOkay(), digitalRead(shutterHall)==LOW, digitalRead(modeInput)==LOW ? "FAIR" : "CHEAT",
    digitalRead(startInput)==LOW, digitalRead(rematchInput)==LOW, digitalRead(10)==LOW, digitalRead(12)==LOW,
    digitalRead(14)==LOW, digitalRead(11)==LOW, digitalRead(13)==LOW, digitalRead(21)==LOW);
}

void command(const char* line) {
  const uint32_t now = millis();
  if (std::strcmp(line,"PING") == 0) { lastHeartbeat = now; status("PONG"); return; }
  if (std::strcmp(line,"STATUS") == 0) { stateReport(); return; }
  if (std::strcmp(line,"STOP") == 0) { cut("FAULT HOST_STOP", true); return; }
  if (std::strcmp(line,"RESET") == 0) {
    if (armed || !contactOkay() || !matches(0)) { status("ERR RESET_CONDITIONS"); return; }
    faulted = false;
    status("OK RESET_DISARMED");
    return;
  }
  if (std::strcmp(line,"ARM") == 0) {
    if (armed || faulted || !contactOkay() || !matches(0) || !thermalOkay()
        || lastHeartbeat == 0 || now-lastHeartbeat >= heartbeatWindow) {
      status("ERR ARM_CONDITIONS"); return;
    }
    armed = true;
    digitalWrite(armOutput,HIGH);
    status("OK ARMED");
    return;
  }
  Profile next;
  char suffix;
  if (std::sscanf(line,"PROFILE %u %u %u %u %u %u %c",&next.pullMs,&next.holdDuty,&next.holdMs,
        &next.settleMs,&next.limitC,&next.beta,&suffix) == 6) {
    if (armed || next.pullMs<10 || next.pullMs>180 || next.holdDuty<1 || next.holdDuty>128
        || next.holdMs<100 || next.holdMs>2000 || next.settleMs<next.pullMs || next.settleMs>350
        || next.limitC<30 || next.limitC>65 || next.beta<2500 || next.beta>5500) {
      status("ERR PROFILE_RANGE"); return;
    }
    profile = next;
    status("OK PROFILE_VOLATILE");
    return;
  }
  unsigned index, pulse;
  if (std::sscanf(line,"SERVO %u %u %c", &index, &pulse, &suffix) == 2) {
    if (!armed || motion != Motion::Idle || index>=5 || pulse<1100 || pulse>1900) {
      status("ERR SERVO_RANGE_OR_STATE"); return;
    }
    setServo(index,pulse);
    status("OK SERVO");
    return;
  }
  if (std::strcmp(line,"RELEASE") == 0 && armed) { curl(now,false); return; }
  if (std::strncmp(line,"THROW ",6) == 0) {
    if (!armed || motion != Motion::Idle || !matches(0)) { status("ERR THROW_STATE"); return; }
    const char* pose = line+6;
    if (std::strcmp(pose,"ROCK")==0) targetMask=0;
    else if (std::strcmp(pose,"SCISSORS")==0) targetMask=1;
    else if (std::strcmp(pose,"PAPER")==0) targetMask=7;
    else { status("ERR POSE"); return; }
    attempt = 0;
    beginThrow(now);
    return;
  }
  status("ERR COMMAND");
}
}

void setup() {
  pinMode(armOutput,OUTPUT);
  digitalWrite(armOutput,LOW);
  pinMode(stopHealthy,INPUT);
  for (uint8_t i=0; i<3; ++i) {
    pinMode(hallExt[i],INPUT);
    pinMode(hallRet[i],INPUT);
    ledcSetup(i,20000,8);
    ledcAttachPin(coilPins[i],i);
    ledcWrite(i,0);
  }
  for (auto pin:{shutterHall,modeInput,startInput,rematchInput}) pinMode(pin,INPUT);
  analogReadResolution(12);
  for (auto pin:thermPins) analogSetPinAttenuation(pin,ADC_11db);

  const mcpwm_io_signals_t signals[] = {MCPWM0A,MCPWM0B,MCPWM1A,MCPWM1B,MCPWM2A};
  for (uint8_t i=0;i<5;++i) mcpwm_gpio_init(MCPWM_UNIT_0,signals[i],servoPins[i]);
  mcpwm_config_t config = {};
  config.frequency=50;
  config.counter_mode=MCPWM_UP_COUNTER;
  config.duty_mode=MCPWM_DUTY_MODE_0;
  for (int i=0;i<3;++i) mcpwm_init(MCPWM_UNIT_0,static_cast<mcpwm_timer_t>(i),&config);
  // Verify horn centers with motor power disconnected before attaching the load.
  for (uint8_t i=0;i<5;++i) setServo(i,1500);
  Serial.begin(115200);
  status("ANIMA_RPS_BENCH DISARMED");
}

void loop() {
  for (int i=0; i<24 && Serial.available(); ++i) {
    const char ch=static_cast<char>(Serial.read());
    if (ch=='\r') continue;
    if (ch=='\n') {
      if (overflow) status("ERR LINE_LENGTH");
      else if (inputLen) { input[inputLen]='\0'; command(input); }
      inputLen=0;
      overflow=false;
    } else if (!overflow && inputLen<sizeof(input)-1) input[inputLen++]=ch;
    else overflow=true;
  }
  if (!armed) return;
  const uint32_t now=millis();
  if (!contactOkay()) { cut("FAULT STOP_AUX",true); return; }
  if (now-lastHeartbeat>=heartbeatWindow) { cut("FAULT HOST_TIMEOUT",true); return; }
  if (now-lastThermal>=60) {
    lastThermal=now;
    if (!thermalOkay()) { cut("FAULT THERMAL_OR_NTC",true); return; }
  }
  serviceMotion(now);
}
