from flask import Flask,request,Blueprint,jsonify,render_template
import pymysql.cursors
from flask_socketio import SocketIO, emit, disconnect

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
@app.errorhandler(Exception)
def exception_handler(e):
    Result = Response("error",-900,"Exception")
    return Result.CreateResponse()

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
            socketio.emit("my_response", {"data": "OK"}, namespace="/test")

        else:
            #　結果の作成
            Result = Response("nodata",-1,"NoAdd")

            # Socketへメッセージを送信
            socketio.emit("my_response", {"data": "NG"}, namespace="/test")

        #結果を返す
        return Result.CreateResponse()

    #except :
    #    return "err"

#-----------------------------------
# 値の表示処理
#-----------------------------------
@app.route("/view")
def ViewData():
    return render_template("view_data.html"
    ,title="値表示"
    ,title_card="センサー値")

#-----------------------------------
# その他
#-----------------------------------
@app.route("/etc")
def ViewEtc():
    return render_template("view_etc.html"
    ,title="その他"
    ,title_card="その他")

#-----------------------------------
#スタートアップ処理
#-----------------------------------
if __name__ == "__main__":
    
    #メインのサーバ起動
    socketio.run(app, host='0.0.0.0', debug=True)

    #app.run(debug=True,host='0.0.0.0')


