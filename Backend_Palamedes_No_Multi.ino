#include <Stepper.h>
#include <AccelStepper.h>
#include <MultiStepper.h>
#include <Servo.h>

//pins
#define X_STEP_PIN 54
#define X_DIR_PIN 55
#define X_ENABLE_PIN 38
#define X_MIN_PIN 3 //we'll use the configuration with only 1 limit switch per axis

#define Y_STEP_PIN 60
#define Y_DIR_PIN 61
#define Y_ENABLE_PIN 56
#define Y_MIN_PIN 14//limit switch 

#define Z_STEP_PIN 46
#define Z_DIR_PIN 48
#define Z_ENABLE_PIN 62
#define Z_MIN_PIN 18 //limit switch

//switch and leds
int Spin=20;
int redPin=57;
int greenPin=58;
int bluePin=63;
int fastBlink=100;
int slowBlink=1000;
int testFlag=0;
long unsigned blinkTimer;
long unsigned previousTime;
//rgb is commun cathode

//commands
String previousOrder="";
String order="";
String command="";
String joint="";
String value="";
String cleanValue="";
int powers[5]={10000,1000,100,10,1};

//variables for interruption
volatile bool failure=false;
int debounceTime = 1200;
long unsigned int lastPress;

//millis to replace delay
unsigned long time_now = 0;
int period = 1000;

AccelStepper stepperX(1, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepperY(1, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper stepperZ(1, Z_STEP_PIN, Z_DIR_PIN);

//MultiStepper steppersControl;  Multi stepper is not used anymore
Servo myservo; //create instance of servo
int pos1=0;//variables for servo
int pos=0;
long gotopositionJ1;
long gotopositionJ2;
long gotoparkingJ1=2000;
long gotoparkingJ2=9000;
//long gotoposition[2];
//long gotoparking[2]={2000,9000};
long gototestJ1=1000;
long gototestJ2=2000;
//long gototest[2]={1000,2000};
long returntotest[2]={0,0};
long zSafety=500;
long zValue;
long lowSpeed = 200;
long highSpeed = 2000;
//variables for reverse kinematics
float L1=228.0; //length of arm1
float L2=135.52; //length of arm2 to be confirmed with solidworks
float theta1A; //angle of joint1
float theta1B;
float theta2A; //angle of joint2
float theta2B;
float phi1; //angle from mooving triangle attached to joint1
float phi2; //angle from XY triangle
float phi3; //angle from mooving triangle attached to joint2

String joint1="";
String joint2="";
String joint3="";
float X;
float Y;
int steps1;
int steps2;
float stepsTheta1;
float stepsTheta2;
bool choice=false;

//to be checked with solidworks
float theta1Max=130;
float theta2Max=104;
float theta1Min=-92;
float theta2Min=-180;

float angleToStepsTheta1 = 88.888;
float angleToStepsTheta2=71.111;
long unsigned baudrate=2000000; 

void setup()
{
  Serial.begin(baudrate);

  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  digitalWrite(redPin,LOW);
  digitalWrite(greenPin,LOW);
  digitalWrite(bluePin,LOW);
   //set motors
   stepperX.setMaxSpeed(1000);
   stepperY.setMaxSpeed(1000);
   stepperZ.setMaxSpeed(1000);

   stepperX.setAcceleration(1000);
   stepperY.setAcceleration(1000);
   stepperZ.setAcceleration(2000);

  //multi stepper control
  //steppersControl.addStepper(stepperX);
  //steppersControl.addStepper(stepperY);

  //set enable pins
   pinMode(X_ENABLE_PIN,OUTPUT);//that's the enbale pin, for some reason it in not defined by the function
   pinMode(Y_ENABLE_PIN,OUTPUT);
   pinMode(Z_ENABLE_PIN,OUTPUT);

  //set limit switch
  pinMode(X_MIN_PIN, INPUT_PULLUP);
  pinMode(Y_MIN_PIN, INPUT_PULLUP);
  pinMode(Z_MIN_PIN, INPUT_PULLUP);
  pinMode(Spin, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(Spin), ISR_button, RISING);
  myservo.attach(11);
  myservo.write(0);
  findStartPosition();

  digitalWrite(greenPin,HIGH);
  blinkTimer=millis();
  while(millis()-blinkTimer <= slowBlink){}
  digitalWrite(greenPin,LOW);

}

void loop()
{
  executer();
}

void executer(){

  //reboot mode
  if(failure==true){
    digitalWrite(greenPin,LOW);
    digitalWrite(bluePin,LOW);
    digitalWrite(redPin,HIGH);
    Serial.end();
    Serial.begin(baudrate);
    String orderCheck="";
    while (failure){
      if(Serial.available()>0){
        orderCheck=Serial.readStringUntil('\r');
        if(orderCheck=="reset"){
          failure=false;
          for (int k=0;k<11;k++){
            digitalWrite(redPin,HIGH);
            blinkTimer=millis();
            while(millis()-blinkTimer <= fastBlink){}
            digitalWrite(redPin,LOW);
            blinkTimer=millis();
            while(millis()-blinkTimer <= fastBlink){}
          }
          
          stepperZ.moveTo(2500);
          //stepperZ.setSpeed(lowSpeed);
          stepperZ.runToPosition();
         
          stepperX.moveTo(gotoparkingJ1);
          stepperY.moveTo(gotoparkingJ2);
          while (stepperX.currentPosition() != gotoparkingJ1 || stepperY.currentPosition() != gotoparkingJ2){
            stepperX.run();
            stepperY.run();
          }
          delay(100);
          Serial.println("ready");
        }
      }
    }
  }

  bool commandFlag=false;
  if(Serial.available()>0){
    order=Serial.readStringUntil('\r');
    commandFlag=true; 
  }

  if (commandFlag && order != previousOrder && failure==false){
    previousOrder = order;
    if (order.substring(0,1)=="J"){
      digitalWrite(bluePin,HIGH);
  	  joint1=order.substring(0,7);
  	  joint2=order.substring(7,14);
  	  joint3=order.substring(14,21);
  	  gotopositionJ1=control(joint1);
  	  gotopositionJ2=control(joint2);
  	  zValue=control(joint3);
      
      if (failure==false){
        stepperZ.moveTo(zSafety);
        stepperZ.setSpeed(lowSpeed);
        stepperZ.runToPosition();
        stepperX.moveTo(gotopositionJ1);
        stepperY.moveTo(gotopositionJ2);
        
        while (stepperX.currentPosition() != gotopositionJ1 || stepperY.currentPosition() != gotopositionJ2 ){
          stepperX.run();
          stepperY.run();
        }
        delay(100);
        stepperZ.moveTo(zValue);
        stepperZ.runToPosition();
        digitalWrite(bluePin,LOW);
        Serial.println("ready");

       }
    }
    if (order.substring(0,1)=="C"){
        findStartPosition();
        Serial.println("ready");
    }
    if (order.substring(0,1)=="X"){
      digitalWrite(redPin,HIGH);
      digitalWrite(bluePin,HIGH);
      X=float(control(order.substring(0,7)));
      Y=float(control(order.substring(7,14)));
      if (order.substring(1,2)=="-"){
        X=-X;
      }
      if (order.substring(8,9)=="-"){
        Y=-Y;
      }
      joint3=order.substring(14,21);
      zValue=control(joint3);

      if(failure==false){
        stepperZ.moveTo(zSafety);
        //stepperZ.setSpeed(lowSpeed);
        stepperZ.runToPosition();
        reverseKinematics(X,Y);
      }
      digitalWrite(redPin,LOW);
      digitalWrite(bluePin,LOW);
      Serial.println("ready");

    }
    if (order.substring(0,1)=="G"){
      digitalWrite(redPin,HIGH);
      digitalWrite(greenPin,HIGH);
      if (order.substring(1,2)=="0"){
        //open gripper angle 0 speed 30ms
        if(myservo.read() != 0 && failure==false){
          moveServo(0,30);
        }
      } 
      else {
        //close gripper angle 42 speed 15
        if (myservo.read() != 42 && failure==false){
          moveServo(42,15);
        }
      }
      digitalWrite(redPin,LOW);
      digitalWrite(greenPin,LOW);
      Serial.println("ready");
    }
  }
}
//changed to long instead of long unsigned
long control(String command){
  joint=command.substring(0,2);
  value=command.substring(2,8);
  int i=0;
  while(value.substring(i,i+1)=="0"){
    i++;
  }
  int cleanPowers[6-(i+1)];
  for (int j=0;j<(6-(i+1));j++){
    cleanPowers[j]=powers[i+j];
  }
  cleanValue=value.substring(i,6);
  long unsigned total=0;
  long unsigned nb=0;
  long unsigned conversion;
  for (int x=0;x<5-i;x++){
    //new lines
    conversion=stringToInt(cleanValue.substring(x,x+1));
    nb=conversion*cleanPowers[x];
    //
    total=total+nb;
  }
  return total;
}

int stringToInt(String myStr){
  int output=0;
  
  if(myStr=="1"){
    output=1;}
  else if(myStr=="2"){
    output=2;}
  else if(myStr=="3"){
    output=3;}
  else if(myStr=="4"){
    output=4;}
  else if(myStr=="5"){
    output=5;}
  else if(myStr=="6"){
    output=6;}
  else if(myStr=="7"){
    output=7;}
  else if(myStr=="8"){
    output=8;}
  else if(myStr=="9"){
    output=9;}
  else if(myStr=="0"){
    output=0;}
  
  return output;
}

void findStartPosition(){
  // move until the switch to find the origin position

  //for X
  while (digitalRead(X_MIN_PIN) != 1) {
    stepperX.setSpeed(-500);//this guy is negative
    stepperX.runSpeed();
  }
  //Serial.println("We found 0 for x");
  stepperX.setCurrentPosition(0); // When limit switch pressed set position to 0 steps
  time_now = millis();
  while(millis() < time_now + period){
    }
  stepperX.moveTo(gotoparkingJ1);//positive
  stepperX.runToPosition();

  
  //for Y
  while (digitalRead(Y_MIN_PIN) != 1) {
    stepperY.setSpeed(-500);//negative
    stepperY.runSpeed();
  }
  stepperY.setCurrentPosition(0); 
  time_now = millis();
  while(millis() < time_now + period){
  }
  stepperY.moveTo(gotoparkingJ2);//positif
  stepperY.runToPosition();

  
  //for Z
  while (digitalRead(Z_MIN_PIN) != 1) {
    stepperZ.setSpeed(-500);//positif c'est ce qu'on avait dit mais la du coup ça a l'ai negatif 
    stepperZ.runSpeed();
  }
  stepperZ.setCurrentPosition(0); 
  time_now = millis();
  while(millis() < time_now + period){
    }
  stepperZ.moveTo(1000);//negatif //le seul qui va pas à un point particulier pour le moment// positif en faite mais cable bleu vers le truc vert 
  stepperZ.runToPosition();
  
}

void reverseKinematics(float X, float Y){
  
    //choosing cardants
  if (X >=0 and Y >=0){
  //1 cardant case
  theta1A=getTheta1A(X,Y);
  theta1B=getTheta1B(X,Y);
  theta2A=getTheta2(X,Y);
  theta2B=-theta2A;
  }
  
  else if (X>=0 and  Y< 0){
  //2 cardant case
  //flip Y
  Y=-Y;
    
  theta1A=getTheta1A(X,Y);
  theta1B=getTheta1B(X,Y);
  theta2A=getTheta2(X,Y);
  theta2B=-theta2A;
  //flip all angles
  theta1A=-theta1A;
  theta1B=-theta1B;
  theta2A=-theta2A;
  theta2B=-theta2B;  
  }
  
  else if (X<0 and Y>=0){
  //3 cardant case
  //flip X
  X=-X;
    
  theta1A=getTheta1A(X,Y);
  theta1B=getTheta1B(X,Y);
  theta2A=getTheta2(X,Y);
  theta2B=-theta2A;
  // transform angles  
  theta1A=180-theta1A;
  theta1B=180-theta1B;
  theta2A=-theta2A;
  theta2B=-theta2B;  
  }
  
  else {
  //4 cardant case
  //X and Y are negative
  X=-X;
  Y=-Y;
  
  theta1A=getTheta1A(X,Y);
  theta1B=getTheta1B(X,Y);
  theta2A=getTheta2(X,Y);
  theta2B=-theta2A;
  //transform angles
  theta1A=-180+theta1A;
  theta1B=-180+theta1B;
  //theta2 stays the same
  }
  //ends of choice of cardants

  //Choosing a couple
  if (choice != true and theta1A <= theta1Max and theta1A >= theta1Min){
    if (theta2A <= theta2Max and theta2A >= theta2Min){
      stepsTheta1=theta1A*angleToStepsTheta1;
      stepsTheta2=theta2A*angleToStepsTheta2;
      choice=!choice;
    }
  }

  if (choice != true and theta1B <= theta1Max and theta1A >= theta1Min){
    if (theta2B <= theta2Max and theta2B >= theta2Min){
      stepsTheta1=theta1B*angleToStepsTheta1;
      stepsTheta2=theta2B*angleToStepsTheta2;
      choice=!choice;
    }
  }
  if (!choice){
    //Serial.println("Destination unreachable");
    for (int k=0;k<11;k++){
            digitalWrite(redPin,HIGH);
            digitalWrite(greenPin,HIGH);
            blinkTimer=millis();
            while(millis()-blinkTimer <= fastBlink){}
            digitalWrite(redPin,LOW);
            digitalWrite(greenPin,LOW);
            blinkTimer=millis();
            while(millis()-blinkTimer <= fastBlink){}
          }
  }

  if(choice){
    steps1=getInt(stepsTheta1);
    steps2=getInt(stepsTheta2);
  }
  
  choice=false; 
  gotopositionJ1= steps1+8000;
  gotopositionJ2= -steps2+7466;

  if(failure==false){
    //steppersControl.moveTo(gotoposition); 
    //steppersControl.runSpeedToPosition();
    stepperX.moveTo(gotopositionJ1);
    stepperY.moveTo(gotopositionJ2);
    while (stepperX.currentPosition() != gotopositionJ1 || stepperY.currentPosition() != gotopositionJ2){
      stepperX.run();
      stepperY.run();
    }
    delay(100);
    Serial.println("J");
    Serial.println(steps1+8000);
    Serial.println(-steps2+7466); 
  }
}

float getTheta1A(float X,float Y){
  //CaseA
  float angle;
  phi2=(180/PI)*acos(X/sqrt(X*X+Y*Y));
  phi1=(180/PI)*acos((L1*L1+X*X+Y*Y-L2*L2)/(2*L1*(sqrt(X*X+Y*Y))));
  angle=phi1+phi2;
  return angle;
}

float getTheta1B(float X,float Y){
  //CaseB
  float angle;
  phi2=(180/PI)*acos(X/sqrt(X*X+Y*Y));
  phi1=(180/PI)*acos((L1*L1+X*X+Y*Y-L2*L2)/(2*L1*(sqrt(X*X+Y*Y))));
  angle=phi2-phi1;
  return angle;
}

float getTheta2(float X,float Y){
   float angle;
   phi3=(180/PI)*acos((L2*L2+L1*L1-(X*X+Y*Y))/(2*L2*L1));
   angle=180-phi3;
   //the 0.3 has been deleted as the solidworks defect doesn't occur in real life
   return angle;
}

int getInt(float value){
  int j=0;
  if (value >=0){
    while(j < value){
      j=j+1;
    }
  }
  else {
    while(j > value){
      j=j-1;
    }
  }
  return j;
}

void moveServo(int angle,int servoSpeed){
  pos=myservo.read();
  if (angle > myservo.read()){
    for(pos=pos1; pos<=angle ; pos++){
      myservo.write(pos);
      pos1=pos;
      previousTime=millis();
      while (millis()-previousTime < servoSpeed){}    
    }
    //going forward
  }
  if(angle < myservo.read()) {
    for(pos; pos>=angle ; pos -=1){
      myservo.write(pos);
      pos1=pos;
      previousTime=millis();
      while (millis()-previousTime < servoSpeed){}
    }
    //going backwards
  }
}

void ISR_button(){
  if ((millis()-lastPress)>debounceTime){
    failure=true;
    lastPress=millis();
    stepperX.stop();
    stepperY.stop();
    stepperZ.stop();
  }
}
