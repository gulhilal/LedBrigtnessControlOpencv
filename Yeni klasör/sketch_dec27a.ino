int ledPin = 3; // led 3. pine bağlı
int serialData=255;// serialData'ya başlangıç değeri olarak 255 atanıyor

void setup() {
  // put your setup code here, to run once:
  pinMode(ledPin,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if(Serial.available()>0)            //seri bağlantı noktasından okunmaya hazır depolanan baytları var ise.
    serialData=Serial.read();        //seri porta gelen değerleri serialData'ya atıyoruz
    analogWrite(ledPin,serialData);  //serialData'daki değeri analog olarak 3. pine yazar.
}
