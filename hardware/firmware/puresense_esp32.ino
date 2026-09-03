// PURESense
// ESP32 Sensor Data Acquisition
//
// Prototype firmware for reading:
// 1. Optical sensor
// 2. Electrical sensor
// 3. Temperature sensor

const int OPTICAL_PIN = 34;
const int ELECTRICAL_PIN = 35;
const int TEMPERATURE_PIN = 4;

void setup() {
  Serial.begin(115200);

  pinMode(OPTICAL_PIN, INPUT);
  pinMode(ELECTRICAL_PIN, INPUT);

  Serial.println("PURESense Sensor System");
  Serial.println("-----------------------");
  Serial.println("Starting sensor acquisition...");
}

void loop() {

  // Read analog sensors
  int optical = analogRead(OPTICAL_PIN);
  int electrical = analogRead(ELECTRICAL_PIN);

  // Temperature sensor reading
  // Actual temperature-sensor library/integration
  // will be added after the selected sensor is finalized.
  float temperature = 0.0;

  // Display readings
  Serial.print("Optical: ");
  Serial.print(optical);

  Serial.print(" | Electrical: ");
  Serial.print(electrical);

  Serial.print(" | Temperature: ");
  Serial.println(temperature);

  delay(1000);
}