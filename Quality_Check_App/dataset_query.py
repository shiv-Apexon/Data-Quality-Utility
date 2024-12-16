import mysql.connector
from mysql.connector import Error
import pyodbc
import pyodbc # For MSSQL
import pymysql # For MySQL
from django.http import JsonResponse
from django.db import connection

def connect_db(db_config):
        host= db_config['host']
        user= db_config['user']
        password= db_config['password']

        conn = pymysql.connect(host=host, user=user, password=password)
        cursor = conn.cursor()
        return cursor

def get_total_rows(table_name):
        cursor = connect_db()
        # 3. Total number of rows in the table
        total_rows_query = f"SELECT COUNT(*) FROM {table_name}"
        cursor.execute(total_rows_query)
        total_rows = cursor.fetchone()[0]
        print(f"Total number of rows in {table_name}: {total_rows}")