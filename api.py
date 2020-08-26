# main.py

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Flask, request, abort
import json
import os

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
    print(lineItem_UsageAccountID)

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
