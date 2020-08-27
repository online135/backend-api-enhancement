# main.py

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Flask, request, abort
from datetime import timedelta, datetime
import json
import os
import sqlite3

db = SQLAlchemy()

app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///aws_usage.sqlite"

db.init_app(app)

@app.route("/aws_usage", methods=['GET'])
def aws_usage():
    
    lineItem_UsageAccountID = request.args.get('lineItem_UsageAccountID')

    if lineItem_UsageAccountID == None:
        return 'please select UsageAccountID'
    
    else:    
        sql_cmd = """
            select product_ProductName, sum(lineItem_Unblendedcost)
            from aws_usage
            where lineItem_UsageAccountID = ?
            group by product_ProductName
            """
        query_data = db.engine.execute(sql_cmd,lineItem_UsageAccountID).fetchall()
        usage_all = json.dumps(dict(query_data))
    
        return usage_all


@app.route("/daily_aws_usage", methods=['GET'])
def daily_aws_usage():
    
    lineItem_UsageAccountID = request.args.get('lineItem_UsageAccountID')

    StartEnd = """
        select service_index, product_ProductName, lineItem_UsageStartDate, lineItem_UsageEndDate, lineItem_UsageAmount
        from aws_usage
        where lineItem_UsageAccountID = ?
        group by service_index
        """

    query_date =db.engine.execute(StartEnd,lineItem_UsageAccountID).fetchall()
    
    TempDictbig = {}
    
    # query_date 為 list 裡面放多個tuple, 格式為 [(編號1, 服務, 起始時間, 結束時間, 使用量),(編號2, 服務, 起始時間, 結束時間, 使用量),(編號3, 服務, 起始時間, 結束時間, 使用量)]
    # query_date[0] 拿出 (編號1, 服務, 起始時間, 結束時間, 使用量)
    # query_date[0][0] 拿出 編號1; query_date[0][1] 拿出服務; query_date[0][2] 拿出起始時間; query_date[0][3] 拿出結束時間; query_date[0][4] 拿出使用量
    # datetime.strptime("2018-01-31", "%Y-%m-%d")

    for i in range(len(query_date)):    

        StartDate = datetime.strptime(query_date[i][2], "%Y-%m-%d")
        EndDate = datetime.strptime(query_date[i][3], "%Y-%m-%d")

        RangeDate = timedelta(days=1)

        j = 0  #總天數
        while StartDate <= EndDate:
            j +=1
            
            StartDate = StartDate + RangeDate

        TempDictsmall = {}
        
        for k in range(j):
            TempTimeFull = str(datetime.strptime(query_date[i][2], "%Y-%m-%d") + timedelta(days=k)).split(' ')
            TempTimeNoHour = TempTimeFull[0] #這個不改, 不要搞混, 變化時間值
            UsageAmount = query_date[i][4]

            try:
                checkbig = TempDictbig[query_date[i][1]]

                for day_had in checkbig:
                    TempDictsmall.update({day_had:checkbig[day_had]})
                    
                if TempTimeNoHour in TempDictsmall.keys():
                    origin = TempDictsmall[TempTimeNoHour]
                    origin += UsageAmount
                    TempDictsmall.update({TempTimeNoHour:origin})


                else:
                    TempDictsmall.update({TempTimeNoHour:UsageAmount})

                TempDictbig.update({query_date[i][1]:TempDictsmall})
                    
            except:
                TempDictsmall.update({TempTimeNoHour:UsageAmount})

        TempDictbig.update({query_date[i][1]:TempDictsmall})

    return(TempDictbig)

@app.route('/')
def index():   

    return 'ok'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
