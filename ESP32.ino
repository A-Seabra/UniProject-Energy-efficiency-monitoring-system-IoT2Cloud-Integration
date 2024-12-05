#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>

#define IO_USERNAME  "ArturSeabra"
#define IO_KEY       ""

char ssid[] = "TP-Link_D0DC";
char pass[] = "a1b2c3d4e5";


#include "AdafruitIO_WiFi.h"

#if defined(USE_AIRLIFT) || defined(ADAFRUIT_METRO_M4_AIRLIFT_LITE) ||         \
    defined(ADAFRUIT_PYPORTAL)

#if !defined(SPIWIFI_SS)
#define SPIWIFI SPI
#define SPIWIFI_SS 10  // Chip select pin
#define SPIWIFI_ACK 9  // a.k.a BUSY or READY pin
#define ESP32_RESETN 6 // Reset pin
#define ESP32_GPIO0 -1 // Not connected
#endif
AdafruitIO_WiFi io(IO_USERNAME, IO_KEY, WIFI_SSID, WIFI_PASS, SPIWIFI_SS,
                   SPIWIFI_ACK, ESP32_RESETN, ESP32_GPIO0, &SPIWIFI);
#else
AdafruitIO_WiFi io(IO_USERNAME, IO_KEY, ssid, pass);
#endif


#define BLYNK_TEMPLATE_ID ""
#define BLYNK_DEVICE_NAME "IoT DTSD"  //ou template?
#define BLYNK_AUTH_TOKEN ""

#define BLYNK_PRINT Serial

#include <WiFi.h>
#include <WiFiClient.h>
#include <BlynkSimpleEsp32.h>



BlynkTimer timer;

#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SH1107 display = Adafruit_SH1107(64, 128, &Wire);

//luz
const int luz = 32;  //4
const float GAMMA = 0.7;
const float RL10 = 50;
char frase_1[20];
char frase_2[20] = "TMax agua 35c";//"Esta de dia";
char frase_3[20] = "TMax agua 28c";//"Esta de noite";
//temperatura
const int temperatura = 34; //0
const float BETA = 3950;
bool ar_condicionado = false;
int ar_condicionado_mode = 0;
int temp_mode = 28;
bool eventTrigger = false;
bool eventTrigger2 = false;
bool eventTrigger3 = false;

AdafruitIO_Feed *Temperatura = io.feed("Temperatura");
//AdafruitIO_Feed *ArCondicionado = io.feed("ArCondicionado");
AdafruitIO_Feed *NivelDeLuz = io.feed("NivelDeLuz");
//AdafruitIO_Feed *TemperaturaLimiteAgua = io.feed("TemperaturaLimiteAgua");


//movimento
const int movimento = 17;

void AdaConnect()
{
  while(! Serial);

  Serial.print("Connecting to Adafruit IO");

  // connect to io.adafruit.com
  io.connect();

  // wait for a connection
  while(io.status() < AIO_CONNECTED) {
    Serial.print(".");
    delay(500);
  }

  // we are connected
  Serial.println();
  Serial.println(io.statusText());
}

void myTimerEvent()
{
  adcAttachPin(luz);
  adcAttachPin(temperatura);
  //RECOLHA DE VALORES*********************************************
  //movimento
  int mov_janela = digitalRead(movimento);
  
  //temperatura
  int analogValue_temperatura_interior = analogRead(temperatura);
  float tensao_interior = analogValue_temperatura_interior/4096.0 *3.3;
  float celsius_interior = -11.6*tensao_interior+50.8-10;
  
  
  //luz
  int analogValue_luz = analogRead(luz);
  float voltage_LUZ = analogValue_luz / 4096. * 3.3;

  //PROCESSAMENTO DE VALORES*****************************************
  //temperatura
  if(celsius_interior < 25){
      ar_condicionado = true;
      ar_condicionado_mode = 1;
  }else{
      if(celsius_interior > 30 or mov_janela == 1){
          ar_condicionado = false;
          ar_condicionado_mode = 0;
      }  
  }
  
  //luz
  if(voltage_LUZ <= 0.97){
    strcpy(frase_1, frase_2);
    temp_mode = 35;
  }else{
    strcpy(frase_1, frase_3);
    temp_mode = 28;
  }

  //PRINT*************************************************************
  display.clearDisplay();
  display.display();
  display.setCursor(0,0);
  Serial.print("Temperatura: ");
  display.print("Temperatura: ");
  Serial.println(celsius_interior);
  display.println(celsius_interior);
  Serial.print("ar condicionado com estado: ");
  display.print("ar condicionado com estado: ");
  Serial.println(ar_condicionado);
  display.println(ar_condicionado);
  Serial.println(frase_1);
  display.println(frase_1);
  display.display();

  Blynk.virtualWrite(V0, celsius_interior);
  Blynk.virtualWrite(V1, ar_condicionado_mode);
  Blynk.virtualWrite(V2, temp_mode);

  if (ar_condicionado_mode == 1 && eventTrigger == false) {
    eventTrigger = true;
    Blynk.logEvent("ar_condicionado", "O ar condicionado está ligado");
  } else if (ar_condicionado_mode == 0) {
    eventTrigger = false;
  }

  if (temp_mode == 28 && eventTrigger2 == false) {
    eventTrigger2 = true;
    eventTrigger3 = false;
    Blynk.logEvent("tmax", "A temperatura máxima da água é agora 28ºC");
  } else if (temp_mode == 35 && eventTrigger3 == false) {
    eventTrigger2 = false;
    eventTrigger3 = true;
    Blynk.logEvent("tmax", "A temperatura máxima da água é agora 35ºC");
  }


  io.run();
  Temperatura->save(celsius_interior);
  //ArCondicionado->save(ar_condicionado_mode);
  //TemperaturaLimiteAgua->save(temp_mode);
  NivelDeLuz->save(voltage_LUZ);
  
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  
  //display 
  Serial.println("128x64 OLED FeatherWing test");
  delay(250); // wait for the OLED to power up
  for(int i=0;i<5;i++){
    display.begin(0x3C, true);
    delay(1000);
    }
  delay(1000);
  display.display();
  delay(1000);
  // Clear the buffer.
  display.clearDisplay();
  display.display();

  display.setRotation(1);

  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
  display.setCursor(0,0);
  display.print("Valores:");
  display.display(); // actually display all of the above

  AdaConnect();
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
  timer.setInterval(5000L, myTimerEvent);
}

void loop() {
  // put your main code here, to run repeatedly:
  Blynk.run();
  timer.run();
}
