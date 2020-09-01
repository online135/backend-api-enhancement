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
    
    try:

        sql_cmd = """
                select product_ProductName, lineItem_UnblendedCost
                from usageAccountID
                where lineItem_UsageAccountID = ?
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
                print('create table usageAccountID')
                
            except:
                print('Had created table daily_usageAccountID')
                
            print('new data:{}'.format(lineItem_UsageAccountID))

            for data in query_data:
                        db.engine.execute('''INSERT INTO usageAccountID(lineItem_usageAccountID, product_ProductName, lineItem_UnblendedCost)
            VALUES (?,?,?)''',(lineItem_UsageAccountID,data[0],data[1]))

            return usage_all


@app.route("/daily_aws_usage", methods=['GET'])
def daily_aws_usage():
    
    lineItem_UsageAccountID = request.args.get('lineItem_UsageAccountID')

    try:
        sql_cmd = """
                select product_productName
                from daily_usageAccountID
                where lineItem_usageAccountID = ?
                """

        service_name = db.engine.execute(sql_cmd,lineItem_UsageAccountID).fetchall()

        test = service_name[0] # the way to test whether the query_data is empty or not.

        showDictBig = {}
        
        for m in range(len(service_name)):
            sql_cmd = """
                    select product_ProductName, lineItem_UsageDate, lineItem_UsageAmount
                    from daily_usageAccountID
                    where lineItem_UsageAccountID = ? and product_ProductName = ?
                    """
            
            query_data2 = db.engine.execute(sql_cmd,lineItem_UsageAccountID, service_name[m][0]).fetchall()

            # query_data (服務1, 日期1, 數量), (服務1, 日期1, 數量), (服務1, 日期3, 數量), (服務1, 日期1, 數量), (服務1, 日期1, 數量), (服務1, 日期3, 數量)
            # query_data[0] (服務1, 日期, 數量), query_data[0][0] 服務1, query_data[0][1] 日期, query_data[0][2] 數量

            showDictSmall = {}

            for n in range(len(query_data2)):
                showDictSmall.update({query_data2[n][1]:query_data2[n][2]})
            showDictBig.update({service_name[m][0]:showDictSmall})
            
        return showDictBig
    
    except:
        lineItem_UsageAccountID = request.args.get('lineItem_UsageAccountID')
        
        StartEnd = """
            select product_ProductName, lineItem_UsageStartDate, lineItem_UsageEndDate, lineItem_UsageAmount
            from aws_usage
            where lineItem_UsageAccountID = ?
            """

        query_data =db.engine.execute(StartEnd,lineItem_UsageAccountID).fetchall()

        #print(query_data)
    
        TempDictBig = {}
    
        # query_data 為 list 裡面放多個tuple, 格式為 [(服務, 起始時間, 結束時間, 使用量),(服務, 起始時間, 結束時間, 使用量),(服務, 起始時間, 結束時間, 使用量)]
        # query_data[0] 拿出 (服務, 起始時間, 結束時間, 使用量)
        # query_data[0][0] 拿出 服務; query_data[0][1] 拿出起始時間; query_data[0][2] 拿出結束時間; query_data[0][3] 拿出使用量
        # datetime.strptime("2018-01-31", "%Y-%m-%d")

        for i in range(len(query_data)):    

            StartDate = datetime.strptime(query_data[i][1], "%Y-%m-%d")
            EndDate = datetime.strptime(query_data[i][2], "%Y-%m-%d")

            RangeDate = timedelta(days=1)

            j = 0  #總天數
        
            while StartDate <= EndDate:
                j +=1
                StartDate = StartDate + RangeDate

            TempDictSmall = {}
                               
            for k in range(j):
                TempTime = str(datetime.strptime(query_data[i][1], "%Y-%m-%d") + timedelta(days=k)).split(' ')[0]  # 取得日期
                UsageAmount = query_data[i][3]

                try:
                    checkBig = TempDictBig[query_data[i][0]]

                    for day_had in checkBig:
                        TempDictSmall.update({day_had:checkBig[day_had]})
                    
                    if TempTime in TempDictSmall.keys():
                        origin = TempDictSmall[TempTime]
                        origin += UsageAmount
                        TempDictSmall.update({TempTime:origin})

                    else:
                        TempDictSmall.update({TempTime:UsageAmount})

                    TempDictBig.update({query_data[i][0]:TempDictSmall})
                    
                except:
                    TempDictSmall.update({TempTime:UsageAmount})                
                    TempDictBig.update({query_data[i][0]:TempDictSmall}) # update algorithms
            #TempDictBig.update({query_data[i][0]:TempDictSmall})

        try:
            sql_cmd = """
                CREATE TABLE daily_usageAccountID(
                lineItem_usageAccountID TEXT,
                product_ProductName TEXT,
                lineItem_UsageDate REAL,
                lineItem_UsageAmount REAl
                )
                """
            db.engine.execute(sql_cmd)
            print('create table daily_usageAccountID')
                
        except:
            print('Had created table daily_usageAccountID')

        print('new data:{}'.format(lineItem_UsageAccountID))
            
        for data in TempDictBig:
            for day in TempDictBig[data]:
                db.engine.execute('''INSERT INTO daily_usageAccountID(lineItem_usageAccountID, product_ProductName, lineItem_UsageDate, lineItem_UsageAmount)
                VALUES (?,?,?,?)''',(lineItem_UsageAccountID,data,day,TempDictBig[data][day]))

        return(TempDictBig)

@app.route('/')
def index():   

    return 'ok'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
