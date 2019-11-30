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
