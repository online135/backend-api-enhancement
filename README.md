# backend-api-enhancement



run api.py

Question 1

Get lineItem/UnblendedCost grouping by product/productname

http://localhost:<port>/api_1?<lineitem/usageaccountid>

example : 
http://127.0.0.1:5000/aws_usage?lineItem_UsageAccountID=120403000000.0

![image](https://ftp.bmp.ovh/imgs/2020/09/de023a5fac52d443.png)
--------
Question 2

Get daily lineItem/UsageAmount grouping by product/productname

http://localhost:<port>/api_2?<lineitem/usageaccountid>

example : 
http://127.0.0.1:5000/daily_aws_usage?lineItem_UsageAccountID=445378576331.0
![image](https://ftp.bmp.ovh/imgs/2020/09/0e34591a728de923.png)

----

Algorithms improved in api1 and api2

1. search the data in database, store the consequence in another table and return the consequence at first time
2. From second time, extract the consequence from the newly created table

When create table, add new data, show some information by using print

=> try this ID : 588275000000.0
http://127.0.0.1:5000/daily_aws_usage?lineItem_UsageAccountID=588275000000.0

----

Use Windows Task Scheduler and script to delete the temporary table every one day

![image](https://ftp.bmp.ovh/imgs/2020/08/58b938c070d78478.png)

Windows Task Scheduler -> db.bat -> deletedb.sql

(Server will reopen every one day. At that time, we can't get data about 10 seconds)

---
version 2020/09/01 17:53 
delete some SQL's "group by" command, speed up the algorithms

=> SQL's searching shorten a little bit
