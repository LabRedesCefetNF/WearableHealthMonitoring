#include <SPI.h> // Comunicação serial síncrona
#include <Wire.h> // Comunicação I2C
#include <SecurityVanet.h> // Comunicação de rede
#include <Ethernet.h> // Configurar e controlar a comunicação Ethernet no Arduino
#include <ArduinoJson.h> // Biblioteca para manipulação de JSON
#include <RTClib.h> // Interage com módulos de relógio em tempo real (RTC)

#define TxPin 12   // Pino de transmissão
#define RxPin 11   // Pino de recepção

SecurityVanet vanet;
RTC_DS3231 rtc;

// Complete com as informações da sua rede
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 113);  // Verificar a disponibilidade de IPs do roteador conectado!

String leituraSensor;
String paciente;
String dataHora;

String sensorReadings[5];  // Array para armazenar as últimas 5 leituras dos sensores
int currentIndex = 0;      // Índice atual para adicionar novas leituras
int numRows = 0; // Declara a variável global para rastrear o número de linhas

// Inicializa o webserver com a porta 80 - porta padrão do HTTP
EthernetServer server(80);

void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);
  while (!Serial);

  vanet.enableRF(TxPin, RxPin);  // Habilitando transmissão RF
  vanet.setKey("0123456789abcdef");  // Definindo senha de transmissão (128 bits)

  if (Ethernet.begin(mac) == 0) {
    Serial.println("Falha ao configurar Ethernet usando DHCP");
    while (true) {
      delay(1);
    }
  }

  if (!rtc.begin()) {
    Serial.println("Não foi possível encontrar o módulo RTC. Verifique a conexão!");
    while (1);
  }

  // Descomente a linha abaixo para ajustar manualmente a hora e a data
  // rtc.adjust(DateTime(2023, 11, 27, 18, 41, 00));

  if (rtc.lostPower()) {
    Serial.println("RTC perdeu a energia! Ajustando a hora e a data...");
    // Ajuste manual da hora e da data
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

  // Inicia a conexão Ethernet e o servidor:
  Ethernet.begin(mac, ip);
  server.begin();
  Serial.print("Servidor está em ");
  Serial.println(Ethernet.localIP());
}

void loop() {
  if (vanet.receiver()) {
    if(digitalRead(13) == HIGH){
      digitalWrite(13, LOW);
    } else {
      digitalWrite(13, HIGH);
    }
    
    String newReading = vanet.getPlainTxt();
    sensorReadings[currentIndex] = newReading;
    currentIndex = (currentIndex + 1) % 5;  // Avança o índice circularmente
    Serial.print(newReading);
    // Extrai o valor do paciente da substring(10)
    paciente = newReading.substring(10);
  } else {
    paciente = sensorReadings[0].substring(10);
  }

  // Fica escutando requisições de novos clientes
  EthernetClient client = server.available();
  if (client) {
    Serial.println("Novo cliente");
    boolean currentLineIsBlank = true;   // Uma solicitação HTTP termina com uma linha em branco
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);
        if (c == '\n' && currentLineIsBlank) {
          // Envia um cabeçalho de resposta HTTP padrão
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: application/json"); // Alterado para JSON
          client.println("Connection: close");  // A conexão será fechada após a conclusão da resposta
          client.println("Refresh: 20");  // Atualiza a página automaticamente a cada 20 segundos
          client.println();

          // Cria um objeto JSON para armazenar os dados
          DynamicJsonDocument doc(1024);
          JsonArray readings = doc.createNestedArray(paciente);

          // Pega a data e hora atual
          DateTime now = rtc.now();

          for (int i = 0; i < 5; i++) {
            int index = (currentIndex + i) % 5;  // Índice circular para as últimas 5 leituras
            String currentReading = sensorReadings[index];
            String paciente = currentReading.substring(10);
            
            // Cria um objeto JSON para cada leitura
            JsonObject reading = readings.createNestedObject();
            reading["paciente"] = paciente;
            reading["dataHora"] = getFormattedTime(now);
            reading["batimentos"] = currentReading.substring(0, 2);
            reading["temperatura"] = currentReading.substring(3, 7);
            String acelerometro = currentReading.substring(8, 9);
            reading["situacao"] = getSituacaoAcelerometro(acelerometro);
          }

          // Serializa o JSON e envia para o cliente
          serializeJson(doc, client);
          break;
        }

        if (c == '\n') {
          currentLineIsBlank = true;  // Começando uma nova linha
        } else if (c != '\r') {
          currentLineIsBlank = false;  // Tendo um caractere na linha atual
        }
      }
    }

    // Fecha a conexão:
    client.stop();
    Serial.println("client disconnected");
  }
}

String getSituacaoAcelerometro(String acelerometro) {
  if (acelerometro == "N") {
    return "De pé";
  } else if (acelerometro == "C") {
    return "Deitado de costas";
  } else if (acelerometro == "B") {
    return "Deitado de bruços";
  } else if (acelerometro == "D") {
    return "Deitado para direita";
  } else if (acelerometro == "E") {
    return "Deitado para esquerda";
  } else {
    return "Deitado de ponta cabeça";
  }
}

String getFormattedTime(DateTime now) {
  String formattedTime = "";

  // Adiciona o dia
  formattedTime += String(now.day());
  formattedTime += "/";

  // Adiciona o mês
  formattedTime += String(now.month());
  formattedTime += "/";

  // Adiciona o ano
  formattedTime += String(now.year());
  formattedTime += " ";

  // Adiciona a hora
  formattedTime += String(now.hour());
  formattedTime += ":";

  // Adiciona o zero à esquerda para o minuto, se necessário
  if (now.minute() < 10) {
    formattedTime += "0";
  }

  // Adiciona o minuto
  formattedTime += String(now.minute());
  formattedTime += ":";

  // Adiciona o zero à esquerda para o segundo, se necessário
  if (now.second() < 10) {
    formattedTime += "0";
  }

  // Adiciona o segundo
  formattedTime += String(now.second());

  return formattedTime;
}

