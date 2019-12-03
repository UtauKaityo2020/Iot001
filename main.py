from flask import Flask,request,Blueprint,jsonify,render_template
import pymysql.cursors
from flask_socketio import SocketIO, emit, disconnect
import datetime
import json

app = Flask(__name__)

# WebSocket初期設定
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)

#-----------------------------------
# 戻り値のクラス
#-----------------------------------
class Response():
    def __init__(self,resType,code,msg):
        self.resType = resType
        self.code = code
        self.msg = msg

    #レスポンス作成
    def CreateResponse(self):
        response = {
            "type":self.resType,
            "code":self.code,
            "msg":self.msg 
        }
        return jsonify(response)

#-----------------------------------
# 例外処理
#-----------------------------------
#@app.errorhandler(Exception)
#def exception_handler(e):
#    Result = Response("error",-900,"Exception")
#    return Result.CreateResponse()

#-----------------------------------
# その他例外
#-----------------------------------
from werkzeug.exceptions import NotFound
bp = Blueprint('exception', __name__)
@bp.errorhandler(NotFound)
def bp_notfound(e):
    Result = Response("error",-900,"NotFoundException")
    return Result.CreateResponse()

#-----------------------------------
# サイトIndex
#-----------------------------------
@app.route("/")
def index():
    return render_template("view_index.html"
    ,title="Iot")

#-----------------------------------
# API処理
#-----------------------------------
@app.route("/send", methods=["GET", "POST"])
def savedata():
    #try:

        strNow = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

        #設定ファイルを読み込む
        app.config.from_json('config.json')

        #Requestを取得
        value1 = ""
        value2 = ""
        value3 = ""
        valueType = ""
        if request.method == "GET":
            valueType = request.args.get('t',default="", type=str)
            value1 = request.args.get('v1',default="", type=str)
            value2 = request.args.get('v2',default="", type=str)
            value3 = request.args.get('v3',default="", type=str)

        Result = ""
        if valueType != "":
            #DB接続 
            connection = pymysql.connect(host=app.config["DB_HOST"],
                                        user=app.config["DB_USER"],
                                        password=app.config["DB_PASS"],
                                        db=app.config["DB_NAME"],
                                        charset=app.config["DB_CHAR_SET"],
                                        # cursorclassを指定することで
                                        # Select結果をtupleではなくdictionaryで受け取れる
                                        cursorclass=pymysql.cursors.DictCursor)

            with connection.cursor() as cursor: 
                sql = "INSERT INTO TBL_VALUE (DATA_TYPE, DATA_VALUE1, DATA_VALUE2, DATA_VALUE3) VALUES (%s, %s, %s ,%s)"
                cursor.execute(sql, (valueType ,value1, value2, value3))
                connection.commit()

            # MySQLから切断する
            connection.close()

            #　結果の作成
            Result = Response("success",1,"OK")

            # Socketへメッセージを送信
            dicRes = {
                "type":"OK",
                "kiatu":value1,
                "situdo":value2,
                "kion":value3,
                "time":strNow
            }
            socketio.emit("ResData", dicRes, namespace="/ViewData")

        else:
            #　結果の作成
            Result = Response("nodata",-1,"NoAdd")

            # Socketへメッセージを送信
            dicRes = {
                "type":"NG",
                "kiatu":"",
                "kion":"",
                "situdo":"",
                "time":strNow
            }
            socketio.emit("ResData", dicRes, namespace="/ViewData")

        #結果を返す
        return Result.CreateResponse()

    #except :
    #    return "err"

#-----------------------------------
# 値の表示処理
#-----------------------------------
@app.route("/view")
def ViewData():

    DateList = CreateDateList()

    return render_template("view_data.html"
    ,title="値表示"
    ,title_card="センサー値"
    ,DateList=DateList)

#-----------------------------------
# 日付一覧の作成
#-----------------------------------
def CreateDateList():

    #設定ファイルを読み込む
    app.config.from_json('config.json')

    connection = pymysql.connect(host=app.config["DB_HOST"],
                                user=app.config["DB_USER"],
                                password=app.config["DB_PASS"],
                                db=app.config["DB_NAME"],
                                charset=app.config["DB_CHAR_SET"],
                                cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor: 
        sql = "SELECT DATE_FORMAT(DATA_TIMESTAMP,'%Y/%m/%d') AS DATE  FROM TBL_VALUE GROUP BY DATE_FORMAT(DATA_TIMESTAMP,'%Y/%m/%d') ORDER BY DATE_FORMAT(DATA_TIMESTAMP,'%Y/%m/%d') DESC"
        cursor.execute(sql)
        result = cursor.fetchall()

    # MySQLから切断する
    connection.close()

    return json.dumps(result)

#-----------------------------------
# 表示データ取得　指定した件数を取得
#-----------------------------------
@app.route("/GetKionTopN", methods=["GET", "POST"])
def GetKionTopN():

    if request.method == "GET":
        Cnt = request.args.get('cnt',default=100, type=int)
    else:
        Cnt = request.form.get('cnt',default=100, type=int)


    #設定ファイルを読み込む
    app.config.from_json('config.json')

    #DB接続
    connection = pymysql.connect(host=app.config["DB_HOST"],
                                user=app.config["DB_USER"],
                                password=app.config["DB_PASS"],
                                db=app.config["DB_NAME"],
                                charset=app.config["DB_CHAR_SET"],
                                cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor: 
        sqlBase = """
            SELECT 
                DATE_YYMMDD_HHII ,
                FORMAT(AVG(DATA_VALUE1),0) AS VAL1,
                FORMAT(AVG(DATA_VALUE2),0) AS VAL2,
                FORMAT(AVG(DATA_VALUE3),0) AS VAL3
            FROM
                (SELECT 
                    DATE_FORMAT(DATA_TIMESTAMP,'%Y/%m/%d %H:%i') AS DATE_YYMMDD_HHII ,
                    DATA_VALUE1,DATA_VALUE2,DATA_VALUE3
                FROM 
                    TBL_VALUE
                WHERE
                    DATA_TYPE = 'BME280'
                ) AS T
            WHERE
                DATA_VALUE1 IS NOT NULL AND
                DATA_VALUE2 IS NOT NULL AND
                DATA_VALUE3 IS NOT NULL
            GROUP BY 
                T.DATE_YYMMDD_HHII
        """
        buf = "SELECT * FROM ({}) AS TBL ORDER BY DATE_YYMMDD_HHII LIMIT {} "
        sql = buf.format(sqlBase,Cnt)

        cursor.execute(sql)
        result = cursor.fetchall()

    # MySQLから切断する
    connection.close()

    return json.dumps(CreateKionJson(result))
    #return sql

#-----------------------------------
# 表示データ取得　指定した条件のレコードを取得
#-----------------------------------
@app.route("/GetKionWhere", methods=["GET", "POST"])
def GetKionWhere():

    strNow = datetime.datetime.now().strftime('%Y/%m/%d')

    if request.method == "GET":
        getDate = request.args.get('Date',default=strNow, type=str)
        stH = request.args.get('StH',default=7, type=int)
        edH = request.args.get('EdH',default=18, type=int)
    else:
        getDate = request.form.get('Date',default=strNow, type=str)
        stH = request.form.get('StH',default=7, type=int)
        edH = request.form.get('WdH',default=18, type=int)

    #日付以外が指定されていた場合は、現在日時を設定する
    if(IsDate(getDate) == False):
        getDate = strNow
    
    #設定ファイルを読み込む
    app.config.from_json('config.json')

    #DB接続
    connection = pymysql.connect(host=app.config["DB_HOST"],
                                user=app.config["DB_USER"],
                                password=app.config["DB_PASS"],
                                db=app.config["DB_NAME"],
                                charset=app.config["DB_CHAR_SET"],
                                cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor: 
        sqlBase = """
            SELECT 
                MAX(DATE_YYMMDD_HHII) AS DATE_YYMMDD_HHII ,
                MAX(DATE_YYYY_MM_DD) AS DATE_YYYY_MM_DD,
                MAX(DATE_HH) AS DATE_HH ,
                MAX(DATE_MM) AS DATE_MM ,
                FORMAT(AVG(DATA_VALUE1),0) AS VAL1,
                FORMAT(AVG(DATA_VALUE2),0) AS VAL2,
                FORMAT(AVG(DATA_VALUE3),0) AS VAL3
            FROM
                (SELECT 
                    DATE_FORMAT(DATA_TIMESTAMP,'%Y/%m/%d %H:%i') AS DATE_YYMMDD_HHII ,
                    DATE_FORMAT(DATA_TIMESTAMP,'%Y/%m/%d') AS DATE_YYYY_MM_DD ,
                    DATE_FORMAT(DATA_TIMESTAMP,'%H') AS DATE_HH ,
                    DATE_FORMAT(DATA_TIMESTAMP,'%i') AS DATE_MM ,
                    DATA_VALUE1,DATA_VALUE2,DATA_VALUE3
                FROM 
                    TBL_VALUE
                WHERE
                    DATA_TYPE = 'BME280'
                ) AS T
            WHERE
                DATA_VALUE1 IS NOT NULL AND
                DATA_VALUE2 IS NOT NULL AND
                DATA_VALUE3 IS NOT NULL
            GROUP BY 
                T.DATE_YYMMDD_HHII
        """
        buf = """
            SELECT 
                * 
            FROM 
                ({}) AS TBL 
            WHERE
                (DATE_YYYY_MM_DD = '{}' AND {} <= DATE_HH)
                AND
                (DATE_YYYY_MM_DD = '{}' AND DATE_HH <= {})
            ORDER BY 
                DATE_YYMMDD_HHII 
            LIMIT 100 
        """
        sql = buf.format(sqlBase,getDate,stH,getDate,edH)
        cursor.execute(sql)
        result = cursor.fetchall()

    # MySQLから切断する
    connection.close()

    return json.dumps(CreateKionJson(result))
    #return sql

#-----------------------------------
# 気温情報のJsonを作成する
#-----------------------------------
def CreateKionJson(pDic):
    Result = {"labels":[],"kion":[],"situdo":[]}
    for item in pDic:
        if IsIntFloat(item["VAL2"]) == True and IsIntFloat(item["VAL3"]) == True:
            Result["labels"].append(item["DATE_YYMMDD_HHII"])
            Result["situdo"].append(float(item["VAL2"]))
            Result["kion"].append(float(item["VAL3"]))

    return Result

#-----------------------------------
# その他
#-----------------------------------
@app.route("/etc")
def ViewEtc():
    return render_template(
        "view_etc.html"
        ,title="その他"
        ,title_card="その他")

#-----------------------------------
# 数字かどうか
#-----------------------------------
def IsIntFloat(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return True

#-----------------------------------
# 日付かどうか
#-----------------------------------
def IsDate(n):
    try:
        datetime.datetime.strptime(n, '%Y/%m/%d')
    except ValueError:
        return False
    else:
        return True

#-----------------------------------
#スタートアップ処理
#-----------------------------------
if __name__ == "__main__":
    
    #メインのサーバ起動
    socketio.run(app, host='0.0.0.0', debug=True)

    #app.run(debug=True,host='0.0.0.0')
