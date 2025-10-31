#include "MPU6050.h"

MPU6050::MPU6050(mpu6050_accel_range_t accelerometerRange, mpu6050_gyro_range_t gyroRange, mpu6050_bandwidth_t bandwidth) {
  // Initialize MPU6050.
  if (!_mpu.begin()) {
    while (1) {
      delay(10);
    }
  }

  _mpu.setAccelerometerRange(accelerometerRange);
  _mpu.setGyroRange(gyroRange);
  _mpu.setFilterBandwidth(bandwidth);
}

void MPU6050::printSetup() {
  printSetupAccelerometer();
  printSetupGyroscope();
  printSetupBandwidth();
}

std::tuple<std::optional<sensors_event_t>, std::optional<sensors_event_t>, std::optional<sensors_event_t>> MPU6050::getSensorData() {
  /* Get new sensor events with the readings */
  sensors_event_t a, g, temp;
  bool result = _mpu.getEvent(&a, &g, &temp);

  // Reading is successful.
  if (result == true) {
    std::optional<sensors_event_t> valid_a = a;
    std::optional<sensors_event_t> valid_g = g;
    std::optional<sensors_event_t> valid_temp = temp;

    return std::make_tuple(valid_a, valid_g, valid_temp);
  }
  else {
    return std::make_tuple(std::nullopt, std::nullopt, std::nullopt);
  }
}

void MPU6050::printSetupAccelerometer() {
  Serial.print("Accelerometer range set to: ");
  switch (_mpu.getAccelerometerRange()) {
  case MPU6050_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case MPU6050_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case MPU6050_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case MPU6050_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }
}

void MPU6050::printSetupGyroscope() {
  Serial.print("Gyro range set to: ");
  switch (_mpu.getGyroRange()) {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }
}

void MPU6050::printSetupBandwidth() {
  Serial.print("Filter bandwidth set to: ");
  switch (_mpu.getFilterBandwidth()) {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }
}