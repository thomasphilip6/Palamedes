#include <Servo.h> //I have error underlines, but the librarie seems to be working
#include <AccelStepper.h>
#include <math.h>


Servo myServo;

//pins
int servoPin = 11;

#define X_STEP_PIN 54
#define X_DIR_PIN 55
#define X_ENABLE_PIN 38
#define X_MIN_PIN 3
#define X_MAX_PIN 2

#define Y_STEP_PIN 60
#define Y_DIR_PIN 61
#define Y_ENABLE_PIN 56
#define Y_MIN_PIN 14
#define Y_MAX_PIN 15

#define Z_STEP_PIN 46
#define Z_DIR_PIN 48
#define Z_ENABLE_PIN 62
#define Z_MIN_PIN 18
#define Z_MAX_PIN 19

AccelStepper stepper1(1, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepper2(1, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper stepper3(1, Z_STEP_PIN, Z_DIR_PIN);

//define variables for the servo/steppers
int servoValue;
int stepper1Value;
int stepper2Value;
int stepper3Value;

long unsigned int previousMillis;

//read the string sent by the GUI in the DIY Robot. We should find how we must modify it in our case
byte inputValue[5];
int k = 0;

String content = "";
int data[10];

double x = 10.0;
double y = 10.0;
double L1 = 228; // L1 = 228mm
double L2 = 136.5; // L2 = 136.5mm
double theta1, theta2, z;


const float theta1AngleToSteps = 44.444444;
const float theta2AngleToSteps = 35.555555;
const float zDistanceToSteps = 100;



void setup() {
  Serial.begin(115200);
//pinmode for the limit switches
  pinMode(X_MIN_PIN, INPUT_PULLUP);
  pinMode(X_MAX_PIN, INPUT_PULLUP);
  pinMode(Y_MIN_PIN, INPUT_PULLUP);
  pinMode(Y_MAX_PIN, INPUT_PULLUP);
  pinMode(Z_MIN_PIN, INPUT_PULLUP);
  pinMode(Z_MAX_PIN, INPUT_PULLUP);

  // Stepper motors max speed
  stepper1.setMaxSpeed(2000);
  stepper1.setAcceleration(2000);
  stepper2.setMaxSpeed(2000);
  stepper2.setAcceleration(2000);
  stepper3.setMaxSpeed(2000);
  stepper3.setAcceleration(2000);

  myServo.attach(11, 600, 2500);
  // initial servo value - open gripper
  data[3] = 180;
  myServo.write(data[3]);
  delay(1000);
  data[2] = 100;
  homing();
}

void loop() {

  if (Serial.available()) {
    content = Serial.readString(); // Read the incomding data from Processing
    // Extract the data from the string and put into separate integer variables (data[] array)
    for (int i = 0; i < 10; i++) {
      int index = content.indexOf(","); // locate the first ","
      data[i] = atol(content.substring(0, index).c_str()); //Extract the number from start to the ","
      content = content.substring(index + 1); //Remove the number from the string
    }
    /*
     data[0] - Joint 1 angle
     data[1] - Joint 2 angle
     data[2] - Z position
     data[3] - Gripper value
     data[4] - Speed value  **NOT NEEDED CONSTANT VALUE**
     data[5] - Acceleration value **NOT NEEDED CONSTANT VALUE**
    */
    }
    stepper1.moveTo(data[0]);
    stepper2.moveTo(data[1]);
    stepper3.moveTo(data[2]);
      while (stepper1.currentPosition() != data[0] || stepper2.currentPosition() != theta2Array[i] || stepper3.currentPosition() != phiArray[i] || stepper4.currentPosition() != zArray[i]) {
        stepper1.run();
        stepper2.run();
        stepper3.run();
        stepper4.run();
      }
    // change speed and acceleration while running the program, now we just set it at max values
    stepper1.setSpeed(2000);
    stepper2.setSpeed(2000);
    stepper3.setSpeed(2000);
    stepper1.setAcceleration(2000);
    stepper2.setAcceleration(2000);
    stepper3.setAcceleration(2000);
  }
