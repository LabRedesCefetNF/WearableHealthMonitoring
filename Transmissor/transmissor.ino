#include <SPI.h> // Comunicação serial síncrona
#include <Wire.h> // Comunicação I2C
#include <SparkFun_ADXL345.h> // Acelerômetro
#include <SecurityVanet.h> // Comunicação de rede

#define batimentos A0
#define temperatura A1
#define TxPin 12                       /*Pino de transmissão*/
#define RxPin 11                       /*Pino de recepção*/

ADXL345 adxl = ADXL345();
SecurityVanet vanet; 

String paciente = "1910ER"; // Máximo e ideal de 6 caracteres

void setup() {
  pinMode(13, OUTPUT);

  vanet.enableRF(TxPin,RxPin);        /*Habilitando transmissão RF*/
  vanet.setKey("0123456789abcdef");   /*Definindo senha de tranmissão
                                        A senha deve possuir 16 caracteres (128bits)*/

  Serial.begin(9600); // Inicializa a comunicação serial
  Wire.begin();
  Serial.println("Iniciar");
  Serial.println();

  adxl.powerOn(); 
  adxl.setRangeSetting(16); // Define o intervalo, valores 2, 4, 8 ou 16
}

void loop() {

  // SENSOR DE BATIMENTOS CARDÍACOS
  // Lê o valor do sensor na porta analógica e converte para tensão
  float bpm = analogRead(batimentos)*5/1023.0;
  bpm = bpm/0.040;
  // Batidas por minutos ideal: entre 50 e 90 bpm
  Serial.print("BATIMENTOS (BPM) - ");
  Serial.print(bpm);
  Serial.println();


  // SENSOR DE TEMPERATURA LM35
  // Lê o valor do sensor na porta analógica e converte para tensão
  float temp = analogRead(temperatura)*5/1023.0;
  // Converte a tensão em °C dividindo ela na escala do sensor
  temp = temp/0.018;
  // Mostra o valor da temperatura no monitor serial. Temperatura ideal: próximo entre 36.5 °C a 37 °C
  Serial.print("TEMPERATURA (°C) - ");
  Serial.print(temp);  
  Serial.println();
  

  // ACELERÔMETRO ADXL345
  // Lê os valores e imprime-os
  int x, y, z;
  adxl.readAccel(&x, &y, &z);
  Serial.print("ACELERÔMETRO - ");
  Serial.print("X:");
  Serial.print(x);
  Serial.print(", ");
  Serial.print("Y:");
  Serial.print(y);
  Serial.print(", ");
  Serial.print("Z:");
  Serial.println(z);

  // Concatena os valores dos sensores para serem enviados para o receptor
  String transmissor = "";
  transmissor.concat(String(bpm,0));
  transmissor.concat("-");
  transmissor.concat(String(temp,1));
  transmissor.concat("-");

  Serial.print("SITUAÇÃO - ");

  if( z > 140 ){
    Serial.println("Deitado de bruços");
    transmissor.concat("B-");
  } else if( ( z > 90 ) && ( y < -50 ) ){
    Serial.println("Deitado de ponta cabeça");
    transmissor.concat("P");
  } else if( ( z > 90 ) && ( y > 15 ) ){
    Serial.println("De pé");
    transmissor.concat("N-");
  } else if( ( z > 90 ) && ( x > 25 ) ){
    Serial.println("Deitado para esquerda");
    transmissor.concat("E-");
  } else if( ( z > 90) && ( x < -45 ) ){
    Serial.println("Deitado para direita");
    transmissor.concat("D-");
  } else {
    Serial.println("Deitado de costas");
    transmissor.concat("C-");
  }

  Serial.print("PACIENTE - ");
  Serial.println(paciente);
  transmissor.concat(paciente);

  // Transmissor 433 MHZ
  vanet.trasmiter(transmissor); /*Enviando mensagem criptografada na rede RF. A mensagem deve possuir 16 caracteres (128bits)*/
  Serial.print("TRANSMISSOR - ");
  Serial.println(transmissor);
  Serial.println();
 
  if(digitalRead(13) == HIGH){
    digitalWrite(13, LOW);
  } else {
    digitalWrite(13, HIGH);
  }
  
  delay(4000); /* Atraso de 4s - Tempo aproximado até a nova atualização 
                da página web com novos dados (total de 5 novos dados)*/
}