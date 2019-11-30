# GETで指定された値を保存する Web API_
使用方法
---
例）
http://example:5000/?t=type&v1=値1&v2=値2&v3=値3

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