int ledPin = 3; // led connected to pin 3
int serialData=255;// SerialData is initialized to 255

void setup() {
  // put your setup code here, to run once:
  pinMode(ledPin,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if(Serial.available()>0)            //if there are bytes stored ready to be read from the serial port.
    serialData=Serial.read();        //assigning values ​​from serial port to serialData
    analogWrite(ledPin,serialData);  //Writes the value in serialData as analog to the 3rd pin.
}
