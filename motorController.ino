#include <Servo.h> //I have error underlines, but the librarie seems to be working
#include <AccelStepper.h>

Servo myservo;

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

int servoValue;
int stepper1Value;
int stepper2Value;
int stepper3Value;

long unsigned int previousMillis;

void setup(){

    Serial.begin(9600);

    myservo.attach(11);

    stepper1.setMaxSpeed(1000);//to be checked with documentation in steps per seconds
    stepper2.setMaxSpeed(1000);//to be checked with documentation
    stepper3.setMaxSpeed(1000);//to be checked with documentation

    stepper1.setCurrentPosition(0);
    stepper2.setCurrentPosition(0);
    stepper3.setCurrentPosition(0);

}

void loop() {

    while(Serial.available()==0){

    }
    servoValue=Serial.readStringUntil(':').toInt();
    stepper1Value=Serial.readStringUntil(':').toInt();
    stepper2Value=Serial.readStringUntil(':').toInt();
    stepper3Value=Serial.readStringUntil('\r').toInt();
}

void movingServo(int servoValue){
    myservo.write(servoValue);
}

void movingStepper(AccelStepper mystepper, int stepperValue){
    mystepper.moveTo(stepperValue);
    mystepper.runToPosition();
}
