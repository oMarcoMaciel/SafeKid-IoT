#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <DNSServer.h>
#include <WebServer.h>
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <stdlib.h>

// --- CONFIGURAÇÃO ---
char mqtt_server[40] = "192.168.1.20"; // Valor padrão
const int mqtt_port = 1883;
const char* tracking_topic_discovery = "tracking/discovery";
const char* mqtt_topic_logs = "logs/esp32";

unsigned long lastScanTime = 0;
const unsigned long scanInterval = 5000; 
bool isScanning = false;

// Pin definitions
#ifndef RC522_SS_PIN
#define RC522_SS_PIN 5
#endif
#ifndef RC522_RST_PIN
#define RC522_RST_PIN 22
#endif
#ifndef LED_RED_PIN
#define LED_RED_PIN 4
#endif
#ifndef LED_GREEN_PIN
#define LED_GREEN_PIN 2
#endif

MFRC522 rfid(RC522_SS_PIN, RC522_RST_PIN);
WiFiClient espClient;
PubSubClient client(espClient);
Preferences preferences;

// Global states for LED feedback (Task 1)
bool ledFeedbackActive = false;
unsigned long ledFeedbackStart = 0;
bool ledFeedbackType = false; // true for Green, false for Red blink

// FreeRTOS Task Handles and Queues (Task 2)
TaskHandle_t mqttTaskHandle = NULL;
TaskHandle_t rfidTaskHandle = NULL;
QueueHandle_t rfidQueue = NULL;
QueueHandle_t logQueue = NULL;

struct RfidScan {
  char uid[32];
};

struct LogMsg {
  char msg[128];
};

void mqtt_log(const char* format, ...) {
  char buffer[128];
  va_list args;
  va_start(args, format);
  vsnprintf(buffer, sizeof(buffer), format, args);
  va_end(args);

  Serial.println(buffer);
  
  if (logQueue != NULL) {
    LogMsg log;
    strncpy(log.msg, buffer, sizeof(log.msg));
    xQueueSend(logQueue, &log, 0);
  }
}

// Flag para salvar config
bool shouldSaveConfig = false;

void saveConfigCallback() {
  Serial.println("Configuração precisa ser salva");
  shouldSaveConfig = true;
}

void setup_wifi_manager() {
  preferences.begin("mqtt-config", false);
  String saved_mqtt = preferences.getString("server", "192.168.1.20");
  strcpy(mqtt_server, saved_mqtt.c_str());

  WiFiManagerParameter custom_mqtt_server("server", "IP do Broker MQTT", mqtt_server, 40);
  WiFiManager wifiManager;

  wifiManager.setSaveConfigCallback(saveConfigCallback);
  wifiManager.addParameter(&custom_mqtt_server);

  // Configura timeout para não travar se o WiFi cair depois
  wifiManager.setConfigPortalTimeout(180); // 3 minutos

  // Tenta conectar com as credenciais padrão primeiro
  WiFi.begin("FAMILIA BATISTA_2G", "ericabatista1601");

  if (!wifiManager.autoConnect("ESP32-Scanner-Config")) {
    Serial.println("Falha ao conectar, reiniciando...");
    delay(3000);
    ESP.restart();
  }

  Serial.println("WiFi Conectado!");
  strcpy(mqtt_server, custom_mqtt_server.getValue());

  if (shouldSaveConfig) {
    preferences.putString("server", mqtt_server);
    Serial.println("Configuração de MQTT salva nas Preferences");
  }
  preferences.end();
}

void scan_tracking_tags() {
  unsigned long now = millis();
  if (now - lastScanTime < scanInterval) return;

  if (!isScanning) {
    Serial.println("Iniciando varredura WiFi assíncrona...");
    WiFi.scanNetworks(true, false, false, 100);
    isScanning = true;
    return;
  }

  int n = WiFi.scanComplete();
  if (n == WIFI_SCAN_FAILED) {
    isScanning = false;
    lastScanTime = now;
    return;
  }
  
  if (n < 0) return; // Scanning still in progress

  Serial.printf("Varredura concluída: %d redes encontradas\n", n);
  
  if (n > 0) {
    for (int i = 0; i < n; ++i) {
      String bssid = WiFi.BSSIDstr(i);
      int rssi = WiFi.RSSI(i);
      
      StaticJsonDocument<128> doc;
      doc["mac"] = bssid;
      doc["rssi"] = rssi;
      doc["scanner"] = "esp32-central";

      char buffer[128];
      serializeJson(doc, buffer);
      client.publish(tracking_topic_discovery, buffer);
    }
  }
  WiFi.scanDelete();
  isScanning = false;
  lastScanTime = now;
}

void updateLedFeedback() {
  if (!ledFeedbackActive) return;
  
  unsigned long now = millis();
  if (ledFeedbackType) { // Green constant
    if (now - ledFeedbackStart > 2000) {
      digitalWrite(LED_GREEN_PIN, LOW);
      ledFeedbackActive = false;
    }
  } else { // Red blinking
    unsigned long elapsed = now - ledFeedbackStart;
    if (elapsed > 1200) {
      digitalWrite(LED_RED_PIN, LOW);
      ledFeedbackActive = false;
    } else {
      // Toggle every 200ms
      digitalWrite(LED_RED_PIN, (elapsed / 200) % 2 == 0);
    }
  }
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  StaticJsonDocument<200> doc;
  if (deserializeJson(doc, message) == DeserializationError::Ok) {
    bool authorized = doc["authorized"];
    ledFeedbackActive = true;
    ledFeedbackStart = millis();
    ledFeedbackType = authorized;
    
    if (authorized) {
      Serial.println("Acesso GARANTIDO");
      digitalWrite(LED_GREEN_PIN, HIGH);
    } else {
      Serial.println("Acesso NEGADO");
      digitalWrite(LED_RED_PIN, HIGH);
    }
  }
}

unsigned long lastReconnectAttempt = 0;

bool reconnect() {
  if (client.connected()) return true;
  
  unsigned long now = millis();
  if (now - lastReconnectAttempt > 5000) {
    lastReconnectAttempt = now;
    Serial.print("Tentando conexão MQTT...");
    String clientId = "ESP32Scanner-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("conectado");
      return true;
    } else {
      Serial.print("falhou, rc=");
      Serial.println(client.state());
    }
  }
  return false;
}

String uidToString(const MFRC522::Uid &uid) {
  String out;
  for (byte i = 0; i < uid.size; i++) {
    if (i) out += ':';
    if (uid.uidByte[i] < 0x10) out += '0';
    out += String(uid.uidByte[i], HEX);
  }
  out.toUpperCase();
  return out;
}

void mqttTask(void *pvParameters) {
  for (;;) {
    if (WiFi.status() == WL_CONNECTED) {
      if (!client.connected()) {
        reconnect();
      }
      client.loop();
      scan_tracking_tags();
      
      // Processa Logs
      LogMsg log;
      if (xQueueReceive(logQueue, &log, 0) == pdTRUE) {
        client.publish(mqtt_topic_logs, log.msg);
      }

      RfidScan scan;
      if (xQueueReceive(rfidQueue, &scan, 0) == pdTRUE) {
        mqtt_log("Enviando UID %s para o broker...", scan.uid);
        StaticJsonDocument<200> doc;
        doc["uid"] = scan.uid;
        char buffer[256];
        serializeJson(doc, buffer);
        client.publish("rfid/scans", buffer);
        
        String responseTopic = String("rfid/responses/") + scan.uid;
        client.subscribe(responseTopic.c_str());
      }
    }
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}

void rfidTask(void *pvParameters) {
  for (;;) {
    updateLedFeedback();
    
    if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
      String uidStr = uidToString(rfid.uid);
      mqtt_log("Cartão detectado! UID: %s", uidStr.c_str());
      RfidScan scan;
      strncpy(scan.uid, uidStr.c_str(), sizeof(scan.uid));
      
      xQueueSend(rfidQueue, &scan, portMAX_DELAY);
      
      rfid.PICC_HaltA();
      rfid.PCD_StopCrypto1();
    }
    vTaskDelay(pdMS_TO_TICKS(50));
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_GREEN_PIN, OUTPUT);
  
  digitalWrite(LED_RED_PIN, LOW);
  digitalWrite(LED_GREEN_PIN, LOW);

  setup_wifi_manager();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqtt_callback);
  client.setBufferSize(256); // Normal buffer size

  SPI.begin(18, 19, 23, 5); // SCK, MISO, MOSI, SS
  rfid.PCD_Init();
  
  rfidQueue = xQueueCreate(10, sizeof(RfidScan));
  logQueue = xQueueCreate(20, sizeof(LogMsg));
  
  xTaskCreatePinnedToCore(mqttTask, "MQTTTask", 8192, NULL, 1, &mqttTaskHandle, 0);
  xTaskCreatePinnedToCore(rfidTask, "RFIDTask", 4096, NULL, 2, &rfidTaskHandle, 1);

  mqtt_log("Scanner Pronto");
}

void loop() {
  vTaskDelete(NULL); 
}
