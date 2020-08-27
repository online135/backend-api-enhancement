# main.py

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Flask, request, abort
from datetime import timedelta, datetime
import json
import os
import sqlite3

i = 0

#        where lineItem_UsageAccountID = 484234000000.0
#        group by product_ProductName

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

    global i
    
    lineItem_UsageAccountID = request.args.get('lineItem_UsageAccountID')

    StartEnd = """
        select service_index, product_ProductName, lineItem_UsageStartDate, lineItem_UsageEndDate, lineItem_UsageAmount
        from aws_usage
        where lineItem_UsageAccountID = ?
        group by service_index
        """

    query_date =db.engine.execute(StartEnd,lineItem_UsageAccountID).fetchall()
    #print(query_date)
    
    TempDictbig = {}
    # query_date 為 list 裡面放多個tuple, 格式為 [(編號1, 服務, 起始時間, 結束時間, 使用量),(編號2, 服務, 起始時間, 結束時間, 使用量),(編號3, 服務, 起始時間, 結束時間, 使用量)]
    # query_date[0] 拿出 (編號1, 服務, 起始時間, 結束時間, 使用量)
    # query_date[0][0] 拿出 編號1; query_date[0][1] 拿出服務; query_date[0][2] 拿出起始時間; query_date[0][3] 拿出結束時間; query_date[0][4] 拿出使用量
    #datetime.strptime("2018-01-31", "%Y-%m-%d")
    #print(len(query_date))

    
    for i in range(len(query_date)):    
        #print(query_date[i])
        #print(query_date[i][0])

        delta = timedelta(days=1)
        total_days = datetime.strptime(query_date[i][3], "%Y-%m-%d") + delta - datetime.strptime(query_date[i][2], "%Y-%m-%d")  # 時間差
        #print(total_days)

        StartDate = datetime.strptime(query_date[i][2], "%Y-%m-%d")
        EndDate = datetime.strptime(query_date[i][3], "%Y-%m-%d")


        RangeDate = timedelta(days=1)

        j = 0  #總天數
        while StartDate <= EndDate:
            j +=1
            
            StartDate = StartDate + RangeDate
            #print(j)

        StartDate = datetime.strptime(query_date[i][2], "%Y-%m-%d")
        EndDate = datetime.strptime(query_date[i][3], "%Y-%m-%d")
        RangeDate = timedelta(days=1)
        
        #for k in range(j):
            #print(datetime.strptime(query_date[i][2], "%Y-%m-%d") + timedelta(days=k))

        conn = sqlite3.connect('aws_usage.sqlite')

        cur = conn.cursor()

        tempProductName = query_date[i][1]  # 選定服務
        #print(tempProductName)

    #cur.execute('DROP TABLE temp')
    

        
        #sql_cmd = '''
        #    CREATE TABLE "temp"(
        #    "TempTime" TEXT,
        #    "UsageAmount" TEXT,
        #    "tempProductName" TEXT
        #    )
        #    '''
        
    #cur.execute(sql_cmd)
        TempDictsmall = {}
        
        for k in range(j):
            #TempTime = str(datetime.strptime(query_date[0][2], "%Y-%m-%d") + timedelta(days=j))
            TempTimeFull = str(datetime.strptime(query_date[i][2], "%Y-%m-%d") + timedelta(days=k)).split(' ')
            print(TempTimeFull)
            print('hi')
            TempTimeNoHour = TempTimeFull[0] #這個不改, 不要搞混
            UsageAmount = query_date[i][4]
            TempDictsmall.update( { TempTimeNoHour : UsageAmount} )
            #cur.execute('''INSERT INTO temp(TempTime,UsageAmount,tempProductName) VALUES (?,?,?)''',(TempTimeNoHour,UsageAmount,tempProductName))
            print(TempDictsmall)
            #conn.commit()
        TempDictbig.update( { query_date[i][1] : TempDictsmall} )
    print(TempDictbig)

    return 'ok'



"""       
    except:
        #UsageAmount = cur.execute('''SELECT UsageAmount FROM Temp''').fetchall()
        #print(UsageAmount)
        #print(TempDict)
        sql_cmd2 = '''
            select TempTime, UsageAmount, tempProductName
            from temp
            group by TempTime
            '''
        query_datatmp = db.engine.execute(sql_cmd2).fetchall()
        print(query_datatmp)
        
        #TempDict = {}
        for j in range(i):
            #TempTime = datetime.strptime(query_date[0][2], "%Y-%m-%d") + timedelta(days=j)
            TempTimeFull = str(datetime.strptime(query_date[0][2], "%Y-%m-%d") + timedelta(days=j)).split(' ')
            TempTimeNoHour = TempTimeFull[0]
            print(TempTimeNoHour)
            UsageAmount = query_date[0][4]
            #for key in TempDict:
            #    if key == TempTimeNoHour:
            #        TempDict[key] += UsageAmount
            #cur.execute('''INSERT INTO temp(TempTime,UsageAmount,tempProductName)
                    #VALUES (?,?,?)''',(TempTime,tempAmount,tempProductName))
"""


@app.route('/')
def index():   
    #sql_cmd = """
    #    select *
    #    from aws_usage
    #    """

    #query_data = db.engine.execute(sql_cmd)
    #print(query_data)
    return 'ok'



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
