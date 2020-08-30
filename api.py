# main.py

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Flask, request, abort
from datetime import timedelta, datetime
import json
import os
import sqlite3

global TempTimeNoHour

db = SQLAlchemy()

app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///aws_usage.sqlite"

db.init_app(app)

@app.route("/aws_usage", methods=['GET'])
def aws_usage():

    lineItem_UsageAccountID = request.args.get('lineItem_UsageAccountID')
    
    try:

        sql_cmd = """
                select product_ProductName, lineItem_UnblendedCost
                from usageAccountID
                where lineItem_UsageAccountID = ?
                group by lineItem_usageAccountID, product_ProductName
                """
        
        query_data = db.engine.execute(sql_cmd,lineItem_UsageAccountID).fetchall()

        test = query_data[0] # the way to test whether the query_data is empty or not.
        
        usage_all = json.dumps(dict(query_data))

        return usage_all
    
    except:
        
        if lineItem_UsageAccountID == None:
            return 'please select UsageAccountID'
    
        else:
            sql_cmd = """
                select product_ProductName, sum(lineItem_Unblendedcost)
                from aws_usage
                where lineItem_UsageAccountID = ?
                group by product_ProductName
                """
            
            # query_data 得到一個 list 裡面有多個 tuple, 整體格式為 [(服務1, Cost1),(服務2, Cost2),(服務3, Cost3),(服務4, Cost4)]
            # query_data[0] 得到 (服務1, Cost1), query_data[0][0] 得到 服務1, query_data[0][1] 得到 Cost1#

            query_data = db.engine.execute(sql_cmd,lineItem_UsageAccountID).fetchall()

            usage_all = json.dumps(dict(query_data)) # return 這個值

            try:
                sql_cmd = """
                    CREATE TABLE usageAccountID(
                    lineItem_usageAccountID TEXT,
                    product_ProductName TEXT,
                    lineItem_UnblendedCost REAL
                    )
                    """
                db.engine.execute(sql_cmd)
                
            except:
                print('new data:{}'.format(lineItem_UsageAccountID))

            for data in query_data:
                        db.engine.execute('''INSERT INTO usageAccountID(lineItem_usageAccountID, product_ProductName, lineItem_UnblendedCost)
            VALUES (?,?,?)''',(lineItem_UsageAccountID,data[0],data[1]))

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

    query_data =db.engine.execute(StartEnd,lineItem_UsageAccountID).fetchall()
    
    TempDictBig = {}
    
    # query_data 為 list 裡面放多個tuple, 格式為 [(編號1, 服務, 起始時間, 結束時間, 使用量),(編號2, 服務, 起始時間, 結束時間, 使用量),(編號3, 服務, 起始時間, 結束時間, 使用量)]
    # query_data[0] 拿出 (編號1, 服務, 起始時間, 結束時間, 使用量)
    # query_data[0][0] 拿出 編號1; query_data[0][1] 拿出服務; query_data[0][2] 拿出起始時間; query_data[0][3] 拿出結束時間; query_data[0][4] 拿出使用量
    # datetime.strptime("2018-01-31", "%Y-%m-%d")

    for i in range(len(query_data)):    

        StartDate = datetime.strptime(query_data[i][2], "%Y-%m-%d")
        EndDate = datetime.strptime(query_data[i][3], "%Y-%m-%d")

        RangeDate = timedelta(days=1)

        j = 0  #總天數
        
        while StartDate <= EndDate:
            j +=1
            StartDate = StartDate + RangeDate

        TempDictSmall = {}

        #try:
        #    checkBig = TempDictBig[query_data[i][1]]
        #                       
        #    for day_had in checkBig:
        #        TempDictSmall.update({day_had:checkBig[day_had]})
        #except:
        #    continue
                               
        for k in range(j):
            TempTimeFull = str(datetime.strptime(query_data[i][2], "%Y-%m-%d") + timedelta(days=k)).split(' ')
            TempTimeNoHour = TempTimeFull[0] #這個不改, 不要搞混, 變化時間值
            UsageAmount = query_data[i][4]

            try:
                checkBig = TempDictBig[query_data[i][1]]

                for day_had in checkBig:
                    TempDictSmall.update({day_had:checkBig[day_had]})
                    
                if TempTimeNoHour in TempDictSmall.keys():
                    origin = TempDictSmall[TempTimeNoHour]
                    origin += UsageAmount
                    TempDictSmall.update({TempTimeNoHour:origin})

                else:
                    TempDictSmall.update({TempTimeNoHour:UsageAmount})

                TempDictBig.update({query_data[i][1]:TempDictSmall})
                    
            except:
                TempDictSmall.update({TempTimeNoHour:UsageAmount})                
                TempDictBig.update({query_data[i][1]:TempDictSmall}) # update algorithms
        #TempDictBig.update({query_data[i][1]:TempDictSmall})

    try:
        sql_cmd = """
            CREATE TABLE daily_usageAccountID(
            lineItem_usageAccountID TEXT,
            product_ProductName TEXT,
            lineItem_UsageTotalDate REAL,
            lineItem_UsageAmount REAl
            )
            """
        db.engine.execute(sql_cmd)
                
    except:
        for data in TempDictBig:
            for day in TempDictBig[data]:
                db.engine.execute('''INSERT INTO daily_usageAccountID(lineItem_usageAccountID, product_ProductName, lineItem_UsageTotalDate, lineItem_UsageAmount)
                VALUES (?,?,?,?)''',(lineItem_UsageAccountID,data,day,TempDictBig[data][day]))

    return(TempDictBig)

@app.route('/')
def index():   

    return 'ok'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
