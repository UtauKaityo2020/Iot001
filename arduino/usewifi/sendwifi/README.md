# ESP-32S_NodeMCU開発ボードを使用して気圧、湿度、温度をWebAPIへ送信する 
clone時の注意
---
Gitからソースを取得した場合、sendwifi.hは含まれません  
wifiへの接続やWebAPIのURLが記載されている為です  
GitからCloneした後に、以下の内容でファイルを作成してください  

sendwifi.h  
```c
#ifndef sendwifi_h
#define sendwifi_h

#include "Arduino.h"

const char* ssid = "hoge";
const char* password = "hoge";
const String HOST = "http://hoge.com/";

#endif
```

機器構成
---
+ HiLetgo ESP32 ESP-32S NodeMCU開発ボード2.4GHz WiFi+Bluetoothデュアルモード  

[Amazon - ESP32S NodeMCU開発ボード](https://www.amazon.co.jp/HiLetgo®-ESP32-ESP-32S-NodeMCU開発ボード2-4GHz-Bluetoothデュアルモード/dp/B0718T232Z/ref=sr_1_4?__mk_ja_JP=カタカナ&keywords=HiLetgo+ESP32+ESP-32S+NodeMCU開発ボード&qid=1575158531&s=industrial&sr=1-4)  
メインのボードです。このボードを中心に構成しています。  

※上記のURLから購入した製品だと、プログラムを書き込む時に手動操作が必要です。スイッチサイエンス等から購入すると自動書き込みのバージョンが送られてくるという噂いています。そちらの購入をお勧めします。  

手動書き込み方法についは、下記サイトで説明されていますので、参考までに。

[ESP32S NodeMCU開発ボードの手動書き込み方法](https://ht-deko.com/arduino/esp-wroom-32.html#04_02)  

+ KeeYees BME280搭載 温湿度 気圧センサーモジュール  

[Amazon - BME280搭載-気圧センサーモジュール](https://www.amazon.co.jp/KeeYees-BME280搭載-気圧センサーモジュール-Arduinoに対応-Raspberry/dp/B07QZWV9Z1/ref=pd_sbs_328_6/355-4325800-0016433?_encoding=UTF8&pd_rd_i=B07QZWV9Z1&pd_rd_r=dba48850-15bb-4550-8d87-e38fc83756a7&pd_rd_w=OWpoA&pd_rd_wg=STmpC&pf_rd_p=1585d594-d9d0-474b-8a4e-69eca1566911&pf_rd_r=286HXJ1FA84NSHNH0XDA&psc=1&refRID=286HXJ1FA84NSHNH0XDA)  
気圧、湿度、温度、華氏を取得するためのモジュールです。I2Cで利用しています。便利です。  
```
I2Cのアドレス：SDO-Low 0x76 / Hight 0x77  
```
ソースでは ```0x76``` を指定してI2C通信を行なっています
