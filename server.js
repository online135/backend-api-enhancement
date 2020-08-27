// imports
var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var sqlite3 = require('sqlite3');
var db = new sqlite3.Database('aws_usage.sqlite');

//mounts BodyParser as middleware - every request passes through it
app.use(bodyParser.urlencoded({ extended: true })); 

// ROUTES

app.get('/', function(req, res) {
    res.send("Get request received at '/' ");
});

app.get('/aws_usage', function(req, res){
    if(req.query.lineItem_UsageAccountId){
        db.all('SELECT product_ProductName, sum(lineItem_Unblendedcost) FROM aws_usage WHERE lineItem_UsageAccountId = ? GROUP BY product_ProductName', 
        [req.query.lineItem_UsageAccountId], function(err, rows){
            if(err){
                res.send(err.message);
            }
            else{
                console.log("Return sum of aws_usages from the lineItem_UsageAccountId: " + req.query.lineItem_UsageAccountId);
                res.json(rows);
                
            }
        });
    }
});


app.listen(3000, function(){
    console.log('Listening on Port 3000');
});
