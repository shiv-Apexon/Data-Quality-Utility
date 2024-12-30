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

CHECK_TYPE_MAP = {
    'NULL': 'NULL Values',
    'STRING': 'Not a String',
    'NUMBER': 'Not a number',
    'DATE': 'Not in Date Format',
    'BOOLEAN': 'Not a Boolean',
    'UNIQUE':'unique values'
}

toaster = ToastNotifier()

def index(request):
    return render(request, 'QCA/home.html')

def data_quality_home(request):
        return render(request, 'QCA/dataqualityhome.html')

def data_ingestion_home(request):
        return render(request, 'QCA/dataingestionhome.html')

def select_platform(request):
        return render(request, 'QCA/select_platform.html')

def dq_report_home(request):
     return render(request,'QCA/dataqualityreport.html')

def custom_page_not_found(request, exception): #for production mode (DEBUG=False)
    return render(request, 'QCA/404.html', status=404)

def connect_db(request):
    message = None

    if request.method == 'POST':
        # Get the user inputs (database host, username, password)
        db_engine = request.POST.get('database_engine')
        host = request.POST.get('host')
        username = request.POST.get('username')
        password = request.POST.get('password')
        connection_name = request.POST.get('connection_name')
        port = request.POST.get('port')
        db_name = request.POST.get('database')

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
                        'db_engine':db_engine,
                        'db_name': None

                        }

                    cursor = connection.cursor()

                    create_schema_query = f"CREATE SCHEMA IF NOT EXISTS dq;"
                    create_table_query = '''
                        CREATE TABLE IF NOT EXISTS dq.connection_info (
                            conn_id INT AUTO_INCREMENT PRIMARY KEY,
                            connection_name VARCHAR(255) NOT NULL,
                            platform VARCHAR(100),
                            host VARCHAR(255),
                            user VARCHAR(255),
                            port INT,
                            password VARCHAR(255),
                            db_name VARCHAR(255)
                        );
                    '''

                    cursor.execute(create_schema_query)
                
                # Use the schema
                    cursor.execute(f"USE dq;")
                    
                    # Create table if it doesn't exist
                    print("Creating table: connection_info")
                    cursor.execute(create_table_query)

                    # SQL query to insert data into the 'connection_info' table
                    insert_query = """
                    INSERT INTO dq.connection_info (connection_name, platform, host, user, port, password, db_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """

                    # Data to be inserted
                    data = (
                        connection_name ,
                        db_engine,
                        host,
                        username ,
                        port ,
                        password ,
                        db_name ,
                    )

                    # Execute the insertion
                    cursor.execute(insert_query, data)
                    # Commit the transaction
                    connection.commit()
                    message = "Successfully connected to the database!"
                    toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds

                    return redirect('/dataqualityhome')                    

                else:
                    message = "Failed to connect to the database."
                    toaster.show_toast("Connection Status", message, duration=2)  # 2 seconds

                connection.close()

            except Error as e:
                # If there is an error, send an appropriate message
                message = f"Error: {e}"
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
                        'db_engine':db_engine,
                        'db_name': None
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
        
        else:
            message = "Other RDBMS are not available yet"
            toaster.show_toast("Connection Status", message, duration=2) 
            return render(request, 'QCA/index.html', {'message': message})

    return render(request, 'QCA/index.html', {'message': message})



@csrf_exempt
def connect_db_with_conn_name(request):
    if request.method == 'POST':
        # Retrieve the connection name from the POST request
        data = json.loads(request.body)       
        # Access the platform value from the parsed data
        conn_name = data.get('conn_name')

        if conn_name:
            try:
                db_config = request.session.get('db_config')
                db_host = db_config['host']
                db_user = db_config['username']
                db_password = db_config['password'] 

                conn = pymysql.connect(host=db_host, user=db_user, password=db_password)
                cursor = conn.cursor()
                with conn.cursor() as cursor:
                    query = '''
                        SELECT host, user, password, platform, db_name, port
                        FROM dq.connection_info
                        WHERE connection_name = %s;
                    '''
                    cursor.execute(query, [conn_name])
                    result = cursor.fetchone()  # Fetch the first row (should be unique by connection_name)

                    if result:
                        # Extract values from the query result
                        host, user, password, platform, db_name, port = result

                        # Store the connection details in the session
                        request.session['db_config'] = {
                            'host': host,
                            'username': user,
                            'password': password,
                            'db_engine': platform, 
                            'db_name': db_name,
                            'port': port
                        }
                        conn.close()
                        print(request.session['db_config'])
                        conn = pymysql.connect(host=host, user=user, password=password)
                        cursor = conn.cursor()
                        # Optionally, return a success response
                        return JsonResponse({"message": "Database connection details stored in session successfully."})

                    else:
                        return JsonResponse({"error": "Connection name not found."}, status=404)
            
            except Exception as e:
                # Handle any exceptions (e.g., database errors)
                return JsonResponse({"error": str(e)}, status=500)

        else:
            return JsonResponse({"error": "No connection name provided."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

def get_all_connections(request):
        # Retrieve the connection name from the POST request

            try:
                db_config = request.session.get('db_config')
                db_host = db_config['host']
                db_user = db_config['username']
                db_password = db_config['password'] 

                conn = pymysql.connect(host=db_host, user=db_user, password=db_password)
                cursor = conn.cursor()
                
                with conn.cursor() as cursor:
                    query = '''
                        SELECT connection_name,platform,db_name,host
                        FROM dq.connection_info
                    '''
                    cursor.execute(query)
                    result = cursor.fetchall()
                    print("----------",result)

            except Exception as e:
                result = []
                print(f"Error fetching data: {e}")
            
            context = {
                'connections': result,
            }    
            print(context)       
            return render(request, "QCA/connection_table.html",context)



def db_info(request):

    db_config = request.session.get('db_config')

    if not db_config:
        message = "Connection is not Established."
        toaster.show_toast("Connection Status", message, duration=2) 
        return redirect('/dataqualityhome')

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
    db_config['db_name'] = db_name
    request.session['db_config'] = db_config
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
def get_columns_and_types(request):

    db_name = request.GET.get('db_name')
    table_name = request.GET.getlist('table_name[]')
    db_config = request.session.get('db_config')

    if table_name == []:
        response = get_tables(request)
        data = json.loads(response.content)  # Convert JSON string to Python dict
        table_name = data.get('tables', [])     
    engine = db_config['db_engine']
    table_and_columns={}

    if db_name and table_name and engine:
       
        if engine == "mysql":
            host = db_config['host']
            user = db_config['username']
            password = db_config['password']

            # Connect to MySQL database
            conn = pymysql.connect(host=host, user=user, password=password, database=db_name)
            cursor = conn.cursor()

            for table in table_name:
                        # Execute query to get column information from MySQL
                        cursor.execute(f"SHOW COLUMNS FROM {table}")
                        columns_info = cursor.fetchall()  # Fetch column details
                        columns = {}

                        # Process each column information
                        for column_info in columns_info:
                            column_name = column_info[0]  # Column name
                            column_type = column_info[1]  # Column data type
                            # Map column types to checkboxes

                            if 'int' in column_type or 'decimal' in column_type:
                                # Numeric types (NULL, NUMBER)
                                columns[column_name] = {
                                    'data_type': 'NUMBER',
                                    'valid_types': ['NULL', 'NUMBER','UNIQUE']
                                }
                            elif 'varchar' in column_type or 'text' in column_type:
                                # String types (NULL, STRING)
                                columns[column_name] = {
                                    'data_type': 'STRING',
                                    'valid_types': ['NULL', 'STRING','UNIQUE']
                                }
                            elif 'date' in column_type or 'datetime' in column_type:
                                # Date types (NULL, DATE)
                                columns[column_name] = {
                                    'data_type': 'DATE',
                                    'valid_types': ['NULL', 'DATE','UNIQUE']
                                }
                            elif 'boolean' in column_type:
                                # Boolean types (NULL, BOOLEAN)
                                columns[column_name] = {
                                    'data_type': 'BOOLEAN',
                                    'valid_types': ['NULL', 'BOOLEAN','UNIQUE']
                                }
                            else:
                                # Default to NULL if the type is unknown or unhandled
                                columns[column_name] = {
                                    'data_type': 'UNKNOWN',
                                    'valid_types': ['NULL']
                                }

                        table_and_columns[table]=columns

                    
    # table_and_columns = {'column_types': {'id':["NULL","NUMBER"], 'check_type':["NULL","STRING"]}, 'employee_details': {'empid':["NULL","NUMBER"], 'name':["NULL","STRING"], 'age':["NULL","NUMBER"], 'gender':["NULL","BOOLEAN"], 'mobile_number':["NULL","NUMBER"]}}

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
                return JsonResponse({'redirect_url': '/dataqualityhome'})
    
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
                return JsonResponse({'redirect_url': '/dataqualityhome'})


@csrf_exempt
def generate_report(request):

    if request.method == 'POST':
        db_config = request.session.get('db_config')
        engine = db_config['db_engine']
        host = db_config['host']
        user = db_config['username']
        password = db_config['password']

        if engine == 'mysql':
            report_data = json.loads(request.POST.get('report_data'))

            db_name = report_data['db_name']
            report = {}
            for table_name, column_types in report_data.items():
                if table_name == 'db_name':
                    continue 
                report[table_name]=[]
                for column_name, checks in column_types.items():
                    # Loop through each check type (the check type is a list, e.g., ["2", "3"])
                    for check in checks:
                        check_type = CHECK_TYPE_MAP.get(check)

                        if check_type:
                            # Generate the SQL query based on the check type
                            sql = generate_check_query(db_name, table_name, column_name, check_type)
                            if check_type == 'unique values':
                                conn = pymysql.connect(host=host, user=user, password=password)
                                with conn.cursor() as cursor:
                                    cursor.execute(sql)
                                    result = cursor.fetchall()
                                if result:
                                    unique_values = [row[0] for row in result]  # Extract the distinct values from the result
                                    unique_count = len(unique_values)  # Get the length of the list
                                    if table_name not in report:
                                        report[table_name] = []
                                    report[table_name].append({
                                        'column_name': column_name,
                                        'check_name': check_type,
                                        'result': unique_count,  # Append the length of the unique values list
                                        'unique_list':unique_values
                                    })
                                    break
                                                    
                            conn = pymysql.connect(host=host, user=user, password=password)
                            with conn.cursor() as cursor:
                                cursor.execute(sql)
                                result = cursor.fetchone()

                            if result:
                                report[table_name].append({
                                    'column_name': column_name,
                                    'check_name': check_type,
                                    'result': result[0]  # assuming result contains the check result
                                })

                total_rows_query = f"SELECT COUNT(*) FROM  {db_name}.{table_name}"
                cursor = conn.cursor()
                cursor.execute(total_rows_query)
                total_rows = cursor.fetchone()[0]
                report[table_name].append({'Total_Rows':total_rows})


        return JsonResponse({'report': render_to_string('QCA/report_template.html', {'report': report})})
            # Render the report HTML using the template and return it as a JSON response

    return JsonResponse({'error': 'Invalid request method'}, status=400)



def generate_check_query(db_name, table_name, column_name, check_type):

    if check_type == 'NULL Values':
        return f"SELECT COUNT(*) FROM {db_name}.{table_name} WHERE {column_name} IS NULL OR {column_name} = '' "
    elif check_type == 'Not a String':
        return f"SELECT COUNT(*) FROM {db_name}.{table_name} WHERE  {column_name} IS NOT NULL AND NOT {column_name} REGEXP '^[a-zA-Z]+$'"
    elif check_type == 'Not a number':
        return f"SELECT COUNT(*) FROM {db_name}.{table_name} WHERE  {column_name} IS NOT NULL AND NOT {column_name} REGEXP '^[0-9]+$'"
    elif check_type == 'Not in Date Format':
        return f"SELECT COUNT(*) FROM {db_name}.{table_name} WHERE  {column_name} IS NOT NULL AND NOT {column_name} REGEXP '^\d{4}-\d{2}-\d{2}$'"
    elif check_type == 'Not a Boolean':
        return f"SELECT COUNT(*) FROM {db_name}.{table_name} WHERE  {column_name} IS NOT NULL AND {column_name} NOT IN ('true', 'false')"
    elif check_type == 'unique values':
        return f"SELECT DISTINCT {column_name} FROM {db_name}.{table_name} WHERE {column_name} IS NOT NULL"
    else:
        return ""
    
def table_exists(table_name,db_name,db_config):

    engine = db_config['db_engine']
    if engine == 'mysql':
            host = db_config['host']
            user = db_config['username']
            password = db_config['password']

            # Set the database connection (if necessary)
            conn = pymysql.connect(host=host, user=user, password=password)
            cursor = conn.cursor()
            with conn.cursor() as cursor:
                cursor.execute(f"USE {db_name};")

                cursor.execute(f"SHOW TABLES LIKE '{table_name}';")
                result = cursor.fetchone()
                conn.commit()

            return result is not None

@csrf_exempt
def save_column_details(request):

    if request.method == "POST":
        db_config = request.session.get('db_config')
        engine = db_config['db_engine']
        if engine == 'mysql':

            report_data = json.loads(request.POST.get('report_data'))
            db_name = 'dq'
            host = db_config['host']
            user = db_config['username']
            password = db_config['password']

            # Set the database connection (if necessary)
            conn = pymysql.connect(host=host, user=user, password=password)
            cursor = conn.cursor()
            cursor.execute(f"USE dq;")
            conn.commit()

            try:
                if not table_exists('column_details',db_name,db_config):
                    with conn.cursor() as cursor:
                        cursor.execute(f"""
                            CREATE TABLE dq.column_details (
                                sr_no INT PRIMARY KEY AUTO_INCREMENT,
                                db_name VARCHAR(255) NOT NULL,
                                table_name VARCHAR(255) NOT NULL,
                                column_name VARCHAR(255) NOT NULL,
                                column_type VARCHAR(255) 
                            );
                        """)

                    conn.commit()

                for table_name, columns in report_data.items():
                        # Skip the 'db_name' key (we only want table data)
                    if table_name == 'db_name':
                        continue
                    cursor.execute("""
                            DELETE FROM dq.column_details 
                            WHERE db_name = %s AND table_name = %s
                        """, [db_name, table_name])
                    conn.commit()

                    for column_name, column_types in columns.items():
                        for column_type in column_types:
                            cursor.execute(f"""
                                    INSERT INTO dq.column_details (db_name, table_name, column_name, column_type)
                                    VALUES ('{db_name}', '{table_name}', '{column_name}', '{column_type}')
                               """)
                            conn.commit()

                return JsonResponse({'message': 'Column details saved successfully!'})
            
            except Exception as e:
                # If there's an error while inserting, return the error message
                return JsonResponse({'error': str(e)}, status=400)
            


@csrf_exempt
def save_quality_check_report(request):

    db_config = request.session.get('db_config')
    engine = db_config['db_engine']
    if request.method == 'POST':
        try:
            if engine == "mysql":
                db_host = db_config['host']
                db_user = db_config['username']
                db_password = db_config['password'] 
                db_name = 'dq'
                report_data = json.loads(request.body)

                report_name = report_data.get('name')
                report_date = report_data.get('timestamp')

                report_str = report_data.get('report')


                report_str = report_str.replace('\\u0027', "'")
                report_str = report_str.replace("'", '"')

                print("-----report-------",report_str)


                try:
                    report_str = json.loads(report_str)
                    print("Report successfully loaded into a dictionary.")

                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")

                print("-----report-------",type(report_str))
                transformed_report = {}

                # Iterate over each key in the report (e.g., 'employee_details', 'column_types', etc.)
                for table_key, table_data in report_str.items():
                    table_transformed = {}

                    # Iterate over each item in the table's list
                    for item in table_data:
                        # Skip the Total_Rows item
                        if "Total_Rows" in item:
                            total_rows = item["Total_Rows"]
                            continue

                        column_name = item["column_name"]
                        # Initialize the column if it doesn't exist
                        if column_name not in table_transformed:
                            table_transformed[column_name] = []

                        # Append the check information (check_name, result, and unique_list if present)
                        column_entry = {
                            "check_name": item["check_name"],
                            "result": item["result"],
                        }
                        if "unique_list" in item:
                            column_entry["unique_list"] = item["unique_list"]

                        table_transformed[column_name].append(column_entry)

                    # Add Total_Rows for the table
                    table_transformed["Total_Rows"] = total_rows

                    # Store the transformed table
                    transformed_report[table_key] = table_transformed


    
    

                conn = pymysql.connect(host=db_host, user=db_user, password=db_password,database=db_name)
                cursor = conn.cursor()


                # Check if the table exists, if not, create it


                # If the table does not exist, create it
                istable_exists = table_exists('quality_checks_reports',db_name,db_config)
                print("-----------\n",istable_exists)

                if not istable_exists:
                    print("----eNTERED LOOp-------\n",istable_exists)


                    cursor.execute(f"""
                        USE dq;
                    """)
                    cursor.execute("""
                        CREATE TABLE dq.quality_checks_reports (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255) UNIQUE NOT NULL,
                            report JSON NOT NULL,
                            date VARCHAR(255)
                        );
                    """)
                    conn.commit()

                # Check if a report with the same name already exists
                cursor.execute("""
                    SELECT id FROM dq.quality_checks_reports WHERE name = %s;
                """,(report_name))

                existing_report = cursor.fetchone()

                if existing_report:
                    return JsonResponse({'message': 'Report with this name already exists.'}, status=400)

                

                report_json = json.dumps(transformed_report)



                # Insert the new report into the table
                cursor.execute("""
                    INSERT INTO quality_checks_reports (name, report,date) VALUES (%s, %s,%s);
                """, (report_name, report_json,report_date))

                # Commit the transaction
                conn.commit()


                return JsonResponse({'message': 'Report saved successfully!'}, status=201)


        except json.JSONDecodeError:
                return JsonResponse({'message': 'Invalid JSON data.'}, status=400)
        
        except Exception as e:
                return JsonResponse({'message': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Invalid request method.'}, status=405)



@csrf_exempt
def get_saved_details(request):

    db_config = request.session.get('db_config')
    engine = db_config['db_engine']
    db_table = 'dq.column_details'
    if request.method == 'GET':
        try:
            if engine == "mysql":
                db_host = db_config['host']
                db_user = db_config['username']
                db_password = db_config['password'] 

                conn = pymysql.connect(host=db_host, user=db_user, password=db_password)
                cursor = conn.cursor()
                cursor.execute(f"USE dq;")

                cursor.execute(f"SHOW TABLES LIKE 'column_details';")
                result = cursor.fetchone()

                istable_exists = result

                if istable_exists:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                                SELECT table_name,column_name, column_type 
                                FROM dq.column_details
                                WHERE db_name = 'dq'
                            """)
        
                        rows = cursor.fetchall()  

                        saved_details = {}

                        for row in rows:
                            db_table, column_name, value = row
                            if db_table not in saved_details:
                                saved_details[db_table] = {}

                            # Check if the column_name already exists, if not, initialize an empty list
                            if column_name not in saved_details[db_table]:
                                saved_details[db_table][column_name] = []

                            # Add the value to the appropriate list, ensuring it's not duplicated
                            if value not in saved_details[db_table][column_name]:
                                saved_details[db_table][column_name].append(str(value))

                return JsonResponse({'saved_details':saved_details})
            
        except:
            pass





@csrf_exempt
def get_conn_name(request):

    data = json.loads(request.body.decode('utf-8'))
    platform = data.get('platform')
    db_config = request.session.get('db_config')
    engine = db_config['db_engine']
    
    if platform:
        try:
            if engine == "mysql":
                db_host = db_config['host']
                db_user = db_config['username']
                db_password = db_config['password'] 

                conn = pymysql.connect(host=db_host, user=db_user, password=db_password)
                cursor = conn.cursor()
            
        # Query the database to get connection names for the selected platform
            with conn.cursor() as cursor:
                query = '''
                    SELECT connection_name
                    FROM dq.connection_info
                    WHERE platform = %s;
                '''
                cursor.execute(query, [platform])
                connections = cursor.fetchall()
                
                # Extract the connection names from the result
                connection_names = [conn[0] for conn in connections]
                
                return JsonResponse({"connections": connection_names})
            
        except Exception as e:
                return print({'message': f'Error: {str(e)}'}, status=500)
    else:  
            return JsonResponse({"connections": []}, status=400)  # If no platform selected, return an empty list

