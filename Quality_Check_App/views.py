import mysql.connector
from mysql.connector import Error
from django.shortcuts import render,redirect
from django.http import HttpResponse
import pyodbc
from win10toast import ToastNotifier
import pyodbc # For MSSQL
import pymysql # For MySQL
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.db import connection
from django.template.loader import render_to_string


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
                    # Save connection info in the session
                    request.session['db_config'] = {
                        'host':host,
                        'username':username,
                        'password':password,
                        'db_engine':db_engine
                        }
                    message = "Successfully connected to the database!"
                    toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds
                    return redirect('db_info')                    

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
                    # Save connection info in the session
                    request.session['db_config'] = {
                        'host':host,
                        'username':username,
                        'password':password,
                        'db_engine':db_engine
                        }

                    message = "Successfully connected to the database!"
                    toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds
                    return redirect('db_info') 

                else:
                    message = "Failed to connect to the database."
                    toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds
                conn.close()
            except Error as e:
                # If there is an error, send an appropriate message
                message = f"Error: Connection Failed"
                toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds
    return render(request, 'QCA/index.html', {'message': message})





def db_info(request):
    db_config = request.session.get('db_config')
    if not db_config:
        return redirect('connect-db')

    host = db_config['host']
    user = db_config['username']
    password = db_config['password']
    engine = db_config['db_engine']

    db_tables = {}

    try:
        # Connect to the database dynamically based on the engine
        if engine == "mssql":
            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};UID={user};PWD={password}"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sys.databases")
            databases = [row[0] for row in cursor.fetchall()]

            for db in databases:
                cursor.execute(f"USE {db}; SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';")
                db_tables[db] = [row[0] for row in cursor.fetchall()]

        elif engine == "mysql":
            conn = pymysql.connect(host=host, user=user, password=password)
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]

            for db in databases:
                cursor.execute(f"USE {db};")
                cursor.execute(f" SHOW TABLES FROM {db};")
                db_tables[db] = [row[0] for row in cursor.fetchall()]

        conn.close()


    except Error as e:
                # If there is an error, send an appropriate message
                message = f"Error fetching databases or tables"
                toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds
                return render(request, "databases.html", {"message": message})
    # Render the result
    return render(request, "QCA/db_info.html", {"db_tables": db_tables})




def get_tables(request):
    db_name = request.GET.get('db_name')
    db_config = request.session.get('db_config')
    host = db_config['host']
    user = db_config['username']
    password = db_config['password']
    engine = db_config['db_engine']
    tables = []

    if db_name and engine:
        try:
            if engine == "mysql":
                # Connect to MySQL database
                conn = pymysql.connect(host=host, user=user, password=password, database=db_name)
                cursor = conn.cursor()
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()

            elif engine == "mssql":
                host = db_config['host']
                user = db_config['username']
                password = db_config['password']
                engine = db_config['db_engine']
                # Connect to MS SQL Server
                conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                                      'SERVER={host};'
                                      f'DATABASE={db_name};'
                                      'UID={user};'
                                      'PWD={password}')
                cursor = conn.cursor()
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()

            # Add other database engines here (PostgreSQL, SQLite, etc.) as needed.

        except Exception as e:
            print(f"Error fetching tables: {str(e)}")

    return JsonResponse({'tables': tables})

# Function to get columns for a specific table in a database
def get_columns(request):
    db_name = request.GET.get('db_name')
    table_name = request.GET.getlist('table_name[]')
    db_config = request.session.get('db_config')

    engine = db_config['db_engine']
    columns = []
    print("-----------------",db_name,table_name)
    if db_name and table_name and engine:
        try:
            if engine == "mysql":
                host = db_config['host']
                user = db_config['username']
                password = db_config['password']

                # Connect to MySQL database
                conn = pymysql.connect(host=host, user=user, password=password, database=db_name)
                cursor = conn.cursor()
                table_and_columns = {}

                for table in table_name:
                    try:
                        # Execute the query to get the columns for the given table
                        cursor.execute(f"SHOW COLUMNS FROM {table}")
                        columns = [row[0] for row in cursor.fetchall()]  # Fetch column names
                        
                        # Save the column names for the current table in the dictionary
                        table_and_columns[table] = columns
                    except Exception as e:
                        # If there is an error fetching the columns (e.g., table does not exist), handle it
                        table_and_columns[table] = f"Error: {str(e)}"
                
                # Close the database connection
                conn.close()

                # Return the columns as a JSON response


            # Add other database engines here (PostgreSQL, SQLite, etc.) as needed.

        except Exception as e:
            print(f"Error fetching columns: {str(e)}")

        return JsonResponse({'table_and_columns': table_and_columns})

@csrf_exempt
def close_connection(request):
    db_config = request.session.get('db_config')
    engine = db_config['db_engine']

        
    if engine == "mysql":
                host = db_config['host']
                user = db_config['username']
                password = db_config['password']

                # Connect to MySQL database
                conn = pymysql.connect(host=host, user=user, password=password)
                conn.close()
                request.session.clear() 
                # Return a JSON response with the redirect URL
                return JsonResponse({'redirect_url': '/connect-db'})
    elif engine == "mssql":
                host = db_config['host']
                user = db_config['username']
                password = db_config['password']
                # Connect to MS SQL Server
                conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                                      'SERVER={host};'
                                      'UID={user};'
                                      'PWD={password}')
                conn.close()
                request.session.clear() 
                return JsonResponse({'redirect_url': '/connect-db'})


@csrf_exempt
def generate_report(request):
    if request.method == 'POST':
        db_config = request.session.get('db_config')
        engine = db_config['db_engine']
        if engine == 'mysql':
            db_name = request.POST.get('db_name')  # Get the database name
            table_name = request.POST.get('table_name')  # Get the table name
            selected_columns = request.POST.getlist('columns[]')  # Get selected columns
            report_data = json.loads(request.POST.get('report_data'))

            host = db_config['host']
            user = db_config['username']
            password = db_config['password']

            # Set the database connection (if necessary)
            conn = pymysql.connect(host=host, user=user, password=password)
            cursor = conn.cursor()
            cursor.execute(f"USE {db_name};")  # Use the specified database

            # Initialize the report dictionary
            report = {}

            # Query each selected column with the conditions
            for column in selected_columns:

                # Get the user-supplied condition for the column, if provided

                # Default WHERE clause for null condition


                # Prepare SQL queries for null, empty, and improper values
                query_null = f"SELECT COUNT(*) FROM {table_name} WHERE {column} IS NULL;"
                query_empty = f"SELECT COUNT(*) FROM {table_name} WHERE {column} = '';"
                query_unique = f"SELECT COUNT(DISTINCT {column}) FROM {table_name} ;"


                # Execute the queries and fetch counts
                cursor.execute(query_null)
                null_count = cursor.fetchone()[0]

                cursor.execute(query_empty)
                empty_count = cursor.fetchone()[0]

                cursor.execute(query_unique)
                unique_count = cursor.fetchone()[0]

                # Add the result for the current column to the report
                report[column] = {
                    'null_count': null_count,
                    'empty_count': empty_count,
                    'unique_count': unique_count,
                }
            print("------------------------------------------------------")
            print(report)
            # Render the report HTML using the template and return it as a JSON response

            return JsonResponse({'report': render_to_string('QCA/report_template.html', {'report': report})})
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def table_exists(table_name,db_config):
    engine = db_config['db_engine']
    if engine == 'mysql':
            host = db_config['host']
            user = db_config['username']
            password = db_config['password']
            db_name = db_config['db_name']

            # Set the database connection (if necessary)
            conn = pymysql.connect(host=host, user=user, password=password)
            cursor = conn.cursor()
            with conn.cursor() as cursor:
                cursor.execute(f"USE {db_name};SHOW TABLES LIKE %s", [table_name])
                result = cursor.fetchone()
            return result is not None

@csrf_exempt
def save_column_details(request):
     
    if request.method == "POST":
        db_config = request.session.get('db_config')
        engine = db_config['db_engine']
        if engine == 'mysql':

            report_data = json.loads(request.POST.get('report_data'))
            print("-----------------",report_data['db_name'])
            db_name = report_data['db_name']

            host = db_config['host']
            user = db_config['username']
            password = db_config['password']

            # Set the database connection (if necessary)
            conn = pymysql.connect(host=host, user=user, password=password)
            cursor = conn.cursor()
            cursor.execute(f"USE {db_name};")
            try:
                if not table_exists('column_details',db_config):
                    with conn.cursor() as cursor:
                        cursor.execute(f"""
                            USE {db_name};
                            CREATE TABLE column_details (
                                sr_no INT PRIMARY KEY AUTO_INCREMENT,
                                db_name VARCHAR(255) NOT NULL,
                                table_name VARCHAR(255) NOT NULL,
                                column_name VARCHAR(255) NOT NULL,
                                column_type INT NOT NULL
                            );
                        """)
                        print("Table 'column_details' created successfully.")
                for table_name, columns in report_data.items():
                        # Skip the 'db_name' key (we only want table data)
                    if table_name == 'db_name':
                        continue
                    for column_name, column_types in columns.items():
                        for column_type in column_types:
                            cursor.execute("""
                                    INSERT INTO column_details (db_name, table_name, column_name, column_type)
                                    VALUES (%s, %s, %s, %s)
                                """, [db_name, table_name, column_name, column_type])
                    return JsonResponse({'message': 'Column details saved successfully!'})
            except Exception as e:
                # If there's an error while inserting, return the error message
                return JsonResponse({'error': str(e)}, status=400)