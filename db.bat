@echo off
taskkill /f /im py.exe
cd C:\Users\b97b0\Desktop\node-sample
sqlite3 aws_usage.sqlite<deletedb.sql
timeout /t 5
START C:\Users\b97b0\Desktop\node-sample\api.py