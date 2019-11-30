from flask import Flask,request,Blueprint,jsonify
import pymysql.cursors

app = Flask(__name__)

#-----------------------------------
#戻り値のクラス
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
#例外処理
#-----------------------------------
@app.errorhandler(Exception)
def exception_handler(e):
    Result = Response("error",-900,"Exception")
    return Result.CreateResponse()

#-----------------------------------
#その他例外
#-----------------------------------
from werkzeug.exceptions import NotFound
bp = Blueprint('exception', __name__)
bp.errorhandler(NotFound)
def bp_notfound(e):
    Result = Response("error",-900,"NotFoundException")
    return Result.CreateResponse()

#-----------------------------------
#API処理
#-----------------------------------
@app.route("/", methods=["GET", "POST"])
def hello():
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
        else:
            #　結果の作成
            Result = Response("nodata",-1,"NoAdd")

        #結果を返す
        return Result.CreateResponse()

    #except :
    #    return "err"

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
