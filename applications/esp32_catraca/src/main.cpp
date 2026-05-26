#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

// ==========================================
// Configurações de Rede (Wi-Fi e MQTT)
// ==========================================
const char* ssid = "NOME_DO_SEU_WIFI";
const char* password = "SENHA_DO_SEU_WIFI";
const char* mqtt_server = "IP_DO_SEU_BROKER"; // Ex: 192.168.0.100 se for local, ou o endereço da AWS
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

// ==========================================
// Configurações do Leitor RFID (MFRC522)
// ==========================================
#define SS_PIN 5   // SDA
#define RST_PIN 21 // RST
MFRC522 rfid(SS_PIN, RST_PIN);

// ==========================================
// Configurações do LED RGB
// ==========================================
#define LED_RED_PIN 12
#define LED_GREEN_PIN 13
#define LED_BLUE_PIN 14

// Declaração das Tasks do FreeRTOS
void TaskRFID(void *pvParameters);
void TaskMQTT(void *pvParameters);

void setup() {
  Serial.begin(115200);
  
  // Configura os pinos do LED
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_BLUE_PIN, OUTPUT);

  // Inicializa barramento SPI e leitor RFID
  SPI.begin();
  rfid.PCD_Init();
  Serial.println("Aproxime o seu cartao/tag RFID...");

  // Criação das Tarefas (Tasks) no FreeRTOS
  // Parâmetros: Função, Nome, Tamanho da Pilha, Parâmetro, Prioridade, Handle
  xTaskCreatePinnedToCore(TaskMQTT, "TaskMQTT", 4096, NULL, 1, NULL, 0); // Roda no Core 0
  xTaskCreatePinnedToCore(TaskRFID, "TaskRFID", 4096, NULL, 1, NULL, 1); // Roda no Core 1
}

void loop() {
  // O FreeRTOS gerencia as tasks, então o loop do Arduino pode ficar vazio
  vTaskDelete(NULL);
}

// ==========================================
// Task 1: Gerenciar Conexão Wi-Fi e MQTT
// ==========================================
void TaskMQTT(void *pvParameters) {
  client.setServer(mqtt_server, mqtt_port);

  for (;;) {
    if (WiFi.status() != WL_CONNECTED) {
      Serial.print("Conectando ao WiFi...");
      WiFi.begin(ssid, password);
      while (WiFi.status() != WL_CONNECTED) {
        vTaskDelay(500 / portTICK_PERIOD_MS);
        Serial.print(".");
      }
      Serial.println(" Conectado!");
    }

    if (!client.connected()) {
      Serial.print("Conectando ao Broker MQTT...");
      String clientId = "ESP32Client-Catraca";
      if (client.connect(clientId.c_str())) {
        Serial.println(" Conectado ao MQTT!");
      } else {
        Serial.print(" Falhou, rc=");
        Serial.print(client.state());
        Serial.println(" Tentando novamente em 5 segundos.");
        vTaskDelay(5000 / portTICK_PERIOD_MS);
      }
    }

    client.loop(); // Mantém a conexão viva
    vTaskDelay(10 / portTICK_PERIOD_MS); // Pequeno atraso para liberar o processador
  }
}

// ==========================================
// Task 2: Ler Cartão RFID e Publicar
// ==========================================
void TaskRFID(void *pvParameters) {
  for (;;) {
    // Verifica se há um novo cartão presente
    if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
      
      String uidString = "";
      for (byte i = 0; i < rfid.uid.size; i++) {
        uidString += String(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
        uidString += String(rfid.uid.uidByte[i], HEX);
      }
      uidString.toUpperCase();
      
      Serial.print("Cartão lido UID: ");
      Serial.println(uidString);

      // Se o MQTT estiver conectado, publica o UID do cartão
      if (client.connected()) {
        String payload = "{\"uid\": \"" + uidString + "\", \"local\": \"Entrada Principal\"}";
        client.publish("escola/catraca/leitura", payload.c_str());
        Serial.println("Enviado via MQTT!");

        // Pisca LED Verde indicando sucesso
        digitalWrite(LED_GREEN_PIN, HIGH);
        vTaskDelay(500 / portTICK_PERIOD_MS);
        digitalWrite(LED_GREEN_PIN, LOW);
      } else {
        // Pisca LED Vermelho indicando falha de rede
        digitalWrite(LED_RED_PIN, HIGH);
        vTaskDelay(500 / portTICK_PERIOD_MS);
        digitalWrite(LED_RED_PIN, LOW);
      }

      // Halt PICC e Stop encryption on PCD
      rfid.PICC_HaltA();
      rfid.PCD_StopCrypto1();
      
      // Atraso de 2 segundos para não ler o mesmo cartão várias vezes seguidas
      vTaskDelay(2000 / portTICK_PERIOD_MS); 
    }
    
    // Pequeno atraso para liberar o processador para outras tarefas
    vTaskDelay(50 / portTICK_PERIOD_MS);
  }
}