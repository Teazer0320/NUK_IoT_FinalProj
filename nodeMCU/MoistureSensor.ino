#define PIN_IN A0
#define PIN_OUT D2
int sensorValue; 

void setup() {
  Serial.begin(9600);
  Serial.println(F("MoistureSensor test!"));
  pinMode(PIN_IN,INPUT);
  pinMode(PIN_OUT,OUTPUT);
}

void loop() {

  sensorValue=analogRead(PIN_IN); //讀取感測器回傳值
  Serial.print("value:");
  Serial.println(sensorValue);
  if(sensorValue<800){
    digitalWrite(PIN_OUT,HIGH);
    Serial.println("PUMP open");
  }
  else{
    digitalWrite(PIN_OUT,LOW);
    Serial.println("PUMP close");
  }
 
  delay(100);
}
