#include <Wire.h>
#include <cactus_io_BME280_I2C.h>
#include <WiFi.h>
#include <HTTPClient.h>

#include "sendwifi.h"
//Gitからソースを取得した場合、sendwifi.hは含まれません
//wifiへの接続やWebAPIのURLが記載されている為です
//GitからCloneした後に、以下の内容でファイルを作成してください
//
//-- sendwifi.h -----------------------------------
//#ifndef sendwifi_h
//#define sendwifi_h
//
//#include "Arduino.h"
//
//const char* ssid = "hoge";
//const char* password = "hoge";
//const String HOST = "http://hoge.com/";
//
//#endif

BME280_I2C bme(0x76);

//-------------
//初期化処理
//-------------
void setup() {

  Serial.begin(115200);
  
  //BME280接続関連
  if (!bme.begin()) { 
    Serial.println("Could not find a valid BME280 sensor, check wiring!"); 
    while (1); 
  } 
  bme.setTempCal(-1);// Temp was reading high so subtract 1 degree 

  //Wifi関連
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");

}

//-------------
//メイン処理
//-------------
void loop() {
  
  bme.readSensor(); 
  
  Serial.print("------------------------------");

  String Kiatu = String(bme.getPressure_MB());
  String Situdo = String(bme.getHumidity());
  String Ondo = String(bme.getTemperature_C());
  String Kasi = String(bme.getTemperature_F());
  
  //シリアルポートへ送信
  Serial.print(Kiatu); Serial.print(" mb\t"); //気圧 
  Serial.print(Situdo); Serial.print(" %\t\t");   //湿度
  Serial.print(Ondo); Serial.print(" *C\t"); //温度
  Serial.print(Kasi); Serial.println(" *F"); //華氏
  
  //サーバへ送信するためのURL作成
  String URL = HOST;
  URL = URL + "?";
  URL = URL + "t=BME280";
  URL = URL + "&";
  URL = URL + "v1=" + Kiatu;
  URL = URL + "&";
  URL = URL + "v2=" + Situdo;
  URL = URL + "&";
  URL = URL + "v3=" + Ondo;

  //サーバへ送信
  HTTPClient http;
  http.begin(URL);
  int httpCode = http.GET();
  
  Serial.printf("URL: %s" , URL.c_str());
  Serial.println();
  Serial.printf("Response: %d", httpCode);
  Serial.println();
  
  // Add a 2 second delay. 
  delay(2000); //just here to slow down the output. 

}
