import mysql.connector
from mysql.connector import Error
from django.shortcuts import render
from django.http import HttpResponse
import pyodbc
from win10toast import ToastNotifier

toaster = ToastNotifier()

def index(request):
    return render(request, 'QCA/index.html')

def connect_db(request):
    message = None


    if request.method == 'POST':
        # Get the user inputs (database host, username, password)
        db_engine = request.POST.get('database_engine')
        host = request.POST.get('host')
        username = request.POST.get('username')
        password = request.POST.get('password')


        if db_engine == 'mysql':
            try:
                # Try to establish a connection using mysql-connector
                connection = mysql.connector.connect(
                    host=host,
                    user=username,
                    password=password
                )
                
                # Check if the connection is successful
                if connection.is_connected():
                    message = "Successfully connected to the database!"
                    toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds
                    

                else:
                    message = "Failed to connect to the database."
                    toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds

                connection.close()

            except Error as e:
                # If there is an error, send an appropriate message
                message = f"Error: Connection Failed"
                toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds


        elif db_engine == 'mssql':
            try:

                # Use pyodbc for MSSQL
                conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};UID={username};PWD={password}'
                conn = pyodbc.connect(conn_str)
                if conn :
                    message = "Successfully connected to the database!"
                    toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds

                else:
                    message = "Failed to connect to the database."
                    toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds
                conn.close()
            except Error as e:
                # If there is an error, send an appropriate message
                message = f"Error: Connection Failed"
                toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds
    return render(request, 'QCA/index.html', {'message': message})
