/*
   ============================================================
   PURESense ESP32 Firmware
   ============================================================

   Reads three analog channels:

   Optical sensor
   Electrical sensor
   Temperature/analog sensor

   Sends readings through Serial.

   IMPORTANT:
   The pin numbers below are example ADC pins.
   Change them to match your actual circuit.
*/


// ============================================================
// SENSOR PINS
// ============================================================

const int OPTICAL_PIN = 34;

const int ELECTRICAL_PIN = 35;

const int TEMPERATURE_PIN = 32;


// ============================================================
// SETUP
// ============================================================

void setup()
{

    Serial.begin(115200);

    delay(1000);


    Serial.println();

    Serial.println(
        "================================"
    );

    Serial.println(
        "PURESense ESP32"
    );

    Serial.println(
        "Multisensor Acquisition System"
    );

    Serial.println(
        "================================"
    );

}


// ============================================================
// READ SENSOR
// ============================================================

float readOptical()
{

    int raw =
        analogRead(
            OPTICAL_PIN
        );


    float voltage =
        (raw / 4095.0) * 3.3;


    return voltage;

}


float readElectrical()
{

    int raw =
        analogRead(
            ELECTRICAL_PIN
        );


    float voltage =
        (raw / 4095.0) * 3.3;


    return voltage;

}


float readTemperature()
{

    int raw =
        analogRead(
            TEMPERATURE_PIN
        );


    float voltage =
        (raw / 4095.0) * 3.3;


    /*
       This is currently an analog
       demonstration conversion.

       Replace this calculation with
       the correct equation for your
       actual temperature sensor.
    */

    float temperature =
        voltage * 10.0;


    return temperature;

}


// ============================================================
// LOOP
// ============================================================

void loop()
{

    float optical =
        readOptical();


    float electrical =
        readElectrical();


    float temperature =
        readTemperature();


    // --------------------------------------------------------
    // Human-readable output
    // --------------------------------------------------------

    Serial.print(
        "Optical: "
    );

    Serial.print(
        optical,
        3
    );


    Serial.print(
        " V"
    );


    Serial.print(
        " | Electrical: "
    );

    Serial.print(
        electrical,
        3
    );


    Serial.print(
        " V"
    );


    Serial.print(
        " | Temperature: "
    );

    Serial.print(
        temperature,
        2
    );


    Serial.println(
        " C"
    );


    // --------------------------------------------------------
    // Machine-readable output
    // --------------------------------------------------------

    Serial.print(
        "DATA,"
    );

    Serial.print(
        optical,
        3
    );

    Serial.print(
        ","
    );

    Serial.print(
        electrical,
        3
    );

    Serial.print(
        ","
    );

    Serial.println(
        temperature,
        2
    );


    delay(1000);

}