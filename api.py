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
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///aws_usage2.sqlite"

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
        select product_ProductName, min(lineItem_UsageStartDate), max(lineItem_UsageEndDate), lineItem_UsageAmount
        from aws_usage
        where lineItem_UsageAccountID = ?
        group by product_ProductName
        """

    query_date =db.engine.execute(StartEnd,lineItem_UsageAccountID).fetchall()
    print(query_date)
    
    # query_date 為 list 裡面放多個tuple, 格式為 [(服務1, 最小日期, 最大日期, 使用量),(服務2, 最小日期, 最大日期, 使用量),(服務3, 最小日期, 最大日期, 使用量)]
    # query_date[0] 拿出 (服務1, 最小日期, 最大日期, 使用量)
    # query_date[0][0] 拿出 服務1; query_date[0][1] 拿出最小日期; query_date[0][2] 拿出最大日期; query_date[0][3] 拿出使用量
    #datetime.strptime("2018-01-31", "%Y-%m-%d")
    print(query_date[0])
    print(query_date[0][0])

    delta = timedelta(days=1)
    total_days = datetime.strptime(query_date[1][2], "%Y-%m-%d") + delta - datetime.strptime(query_date[1][1], "%Y-%m-%d")
    print(total_days)

    StartDate = datetime.strptime(query_date[1][1], "%Y-%m-%d")
    EndDate = datetime.strptime(query_date[1][2], "%Y-%m-%d")


    RangeDate = timedelta(days=1)

    i = 0  #天數
    while StartDate <= EndDate:
        i +=1
            
        StartDate = StartDate + RangeDate
    print(i)

    StartDate = datetime.strptime(query_date[1][1], "%Y-%m-%d")
    EndDate = datetime.strptime(query_date[1][2], "%Y-%m-%d")
    RangeDate = timedelta(days=1)
        
    for j in range(i):
        print(datetime.strptime(query_date[1][1], "%Y-%m-%d") + timedelta(days=j))

    conn = sqlite3.connect('aws_usage.sqlite')

    cur = conn.cursor()

    tempProductName = query_date[1][0]
    print(tempProductName)

    cur.execute('DROP TABLE temp')
    
    try:
        
        sql_cmd = '''
            CREATE TABLE "temp"(
            "TempTime" TEXT,
            "UsageAmount" TEXT,
            "tempProductName" TEXT
            )
            '''
        
        cur.execute(sql_cmd)
        
        for j in range(i):
            TempTime = datetime.strptime(query_date[1][1], "%Y-%m-%d") + timedelta(days=j)
            UsageAmount = query_date[1][3] / i
            cur.execute('''INSERT INTO temp(TempTime,UsageAmount,tempProductName) VALUES (?,?,?)''',(TempTime,UsageAmount,tempProductName))

            conn.commit()
    except:
        UsageAmount = cur.execute('''SELECT UsageAmount FROM Temp''').fetchall()
        print(UsageAmount)
        for j in range(i):
            TempTime = datetime.strptime(query_date[1][1], "%Y-%m-%d") + timedelta(days=j)
            tempAmount = float(UsageAmount[1][0]) + query_date[1][3] / i
#            UsageAmount[k][0] = list(UsageAmount[k][0])
#            UsageAmount[k][0] = float(UsageAmount[k][0]) + query_date[i][3] / j
            cur.execute('''INSERT INTO temp(TempTime,UsageAmount,tempProductName)
                    VALUES (?,?,?)''',(TempTime,tempAmount,tempProductName))
                
    return 'ok'


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
