# -*- coding: utf-8 -*-
"""
Created on Tuseday August 25 2020
@author: online135
"""

import sqlite3
import csv

conn = sqlite3.connect('aws_usage.sqlite')

cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS bill')
cur.execute('''
CREATE TABLE "bill"(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    "PayerAccountId" REAL
)
''')

cur.execute('DROP TABLE IF EXISTS lineItem')
cur.execute('''
CREATE TABLE "lineItem"(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    "UnblendedCost"  REAL,
    "UnblendedRate"   REAL,
    "UsageAccountId"    REAL,
    "UsageAmount"    REAL,
    "UsageStartDate"    TEXT,
    "UsageEndDate"  TEXT
)
''')

cur.execute('DROP TABLE IF EXISTS product')
cur.execute('''
CREATE TABLE "product"(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    "ProductName"   TEXT
)
''')



fname=input('Enter the aws csv file name: ')
if len(fname) < 1 : fname="output.csv"

with open(fname) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        bill_PayerAccountId=float(row[5])                  # The account ID of the paying account. For an organization in AWS Organizations, this is the account ID of the master account.
        lineItem_UnblendedCost=float(row[19])               # The UnblendedCost is the UnblendedRate multiplied by the UsageAmount.

        if row[18] == '':
            lineItem_UnblendedRate=''
        else:
            lineItem_UnblendedRate=float(row[18])              # The uncombined rate for specific usage. For line items that have an RI discount applied to them, the UnblendedRate is zero. Line items with an RI discount have a UsageType of Discounted Usage.

        lineItem_UsageAccountId=float(row[7])              # The ID of the account that used this line item. For organizations, this can be either the master account or a member account. You can use this field to track costs or usage by account.
        lineItem_UsageAmount=float(row[15])          # The amount of usage that you incurred during the specified time period. For size-flexible reserved instances, use the reservation/TotalReservedUnits column instead.

        StartDate = row[9].split("T", 1)
        lineItem_UsageStartDate=StartDate[0]       # The start date and time for the line item in UTC, inclusive. The format is YYYY-MM-DDTHH:mm:ssZ.

        EndDate = row[10].split("T", 1)
        lineItem_UsageEndDate=EndDate[0]       # The end date and time for the corresponding line item in UTC, exclusive. The format is YYYY-MM-DDTHH:mm:ssZ.

        product_ProductName=row[21]           # The full name of the AWS service. Use this column to filter AWS usage by AWS service. Sample values: AWS Backup, AWS Config, Amazon Registrar, Amazon Elastic File System, Amazon Elastic Compute Cloud
        cur.execute('''INSERT INTO bill(ID,PayerAccountId) VALUES (?,?);''',(None,bill_PayerAccountId))
    
        
        cur.execute('''INSERT INTO lineItem(ID,UnblendedCost,UnblendedRate,UsageAccountId,UsageAmount,UsageStartDate,UsageEndDate)
            VALUES (?,?,?,?,?,?,?)''',(None,lineItem_UnblendedCost,lineItem_UnblendedRate,lineItem_UsageAccountId,lineItem_UsageAmount,lineItem_UsageStartDate,lineItem_UsageEndDate))

        cur.execute('''INSERT INTO product(ID,ProductName)
            VALUES (?,?)''',(None,product_ProductName))

        conn.commit()

conn.close()
print('done')
