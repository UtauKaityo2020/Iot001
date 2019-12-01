# GETで指定された値を保存する Web API

[ESP32](https://docs.zerynth.com/latest/official/board.zerynth.nodemcu_esp32/docs/index.html)で取得した湿度や温度をWeb上DBに保存する為に作りました。  
ESP32内で、当WebAPIに値をPOST(実際はGET送信)して値をWeb上のDBに送信して保存します。

使用方
---
例）
http://example:5000/send?t=type&v1=値1&v2=値2&v3=値3

保存されるテーブルと各値が保存されるフィールド名
---
テーブル名：TBL_VALUE 

引数1： t  
データのタイプ → DATA_TYPE
 
引数2： v1  
値１ → DATA_VALUE1  
 
引数3： v2  
値２ → DATA_VALUE2  
 
引数4： v3  
値３ → DATA_VALUE3  

設定ファイル
---
ソースを実行するには、以下の設定ファイルが必要です。  
 
config.json  

``` json
{
    "DB_NAME":"DB名",
    "DB_HOST":"localhost",
    "DB_USER":"DBのログインID",
    "DB_PASS":"DBのパスワード",
    "DB_CHAR_SET":"utf8"
}
```

当WebAPIを利用するESP32用のソースについて
---
以下のフォルダに設置
<pre>
arduino  
　└ usewifi  
　　　└ sendwifi
　　　　　├ README.md
　　　　　: 
</pre>

環境
---
+ Python v3.7.3
+ Flask v1.1.1
+ mysql v8.0.18
+ Bootstrap v4.4.1
+ jquery.mini v3.4.1

Flaskで使用しているライブラリ
---
+ PyMySQL ...DB接続用
+ flask_socketio ...websocket用

※ライブラリをインストールする方法  

(例)   
```pip insutall PyMySQL```
