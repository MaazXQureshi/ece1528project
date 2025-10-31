#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <tuple>
#include <optional>

class MPU6050 {
  public:
    MPU6050(mpu6050_accel_range_t accelerometerRange, mpu6050_gyro_range_t gyroRange, mpu6050_bandwidth_t bandwidth);
    void printSetup();

    /**
     * Returns:
     * 1. Acceleration.
     * 2. Rotation Angle.
     * 3. Temperature.
     */
    std::tuple<std::optional<sensors_event_t>, std::optional<sensors_event_t>, std::optional<sensors_event_t>> getSensorData();

  private:
    void printSetupAccelerometer();
    void printSetupGyroscope();
    void printSetupBandwidth();

    Adafruit_MPU6050 _mpu;
};
