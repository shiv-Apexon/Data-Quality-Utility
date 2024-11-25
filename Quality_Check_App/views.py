from django.shortcuts import render, redirect
import mysql.connector
import ast
from win10toast import ToastNotifier
from django.db.utils import OperationalError, ProgrammingError

toaster = ToastNotifier()
RUN_ONCE = False

# View for the credentials form page
def credentials_form(request):
    if request.method == "POST":
        # Get credentials from the form
        database = request.POST.get('engine')#main RDBMS
        hostname = request.POST.get('hostname')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Store the credentials in the session or elsewhere
        request.session['db_conn_details'] = {
            'database': database,
            'hostname': hostname,
            'username': username,
            'password': password
        }
        global RUN_ONCE
        RUN_ONCE = False
        # After the form is submitted, redirect to the select_database page
        return redirect('select_database')  # Correct redirect to select_database URL

    return render(request, 'QCA/credentials_form.html')  # Render the form if GET request

#Helper function to connect to the mysql db
def _get_mysql_connection(request):
    # Retrieve connection details from session
    conn_details = request.session.get('db_conn_details')
    if not conn_details:
        return None  # If no connection details, redirect to the credentials form
    host = conn_details['hostname']
    username = conn_details['username']
    password = conn_details['password']

    try:
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password
        )
        return conn
    except Exception as e:
        message = "Failed to connect to the database."
        toaster.show_toast("Connection Status", message, duration=2)
        return None
        # context = {
        #     'message':message
        # }
        # return render(request, 'QCA/credentials_form.html',context)

# View for selecting the database, table, and columns
def select_database(request):
    conn_details = request.session.get('db_conn_details')
    global RUN_ONCE
    if conn_details['database']=='mysql':
    # Get MySQL connection
        try:
            conn = _get_mysql_connection(request)
            if not conn:
                context = {
                    'message': "Failed to connect to the database."
                }
                return render(request, 'QCA/credentials_form.html',context)  # If no connection, redirect to credentials form

            if RUN_ONCE == False:
                message = "Connected to the Mysql successfully"
                toaster.show_toast("Connection Status", message, duration=2)
                RUN_ONCE = True

            cursor = conn.cursor()

            # Fetch the list of databases
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]

            #Database name inside mysql
            selected_database = request.GET.get('database')
            # print("---------------------44444------------------",selected_database)
            tables = []
            columns = []
            selected_table = []
            selected_columns = []

            if selected_database:
                selected_table = []
                tables.clear()
                columns.clear()
                # Select the database
                cursor.execute(f"USE {selected_database};")

                # Fetch the list of tables
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]

                selected_table = request.GET.get('table')
                if selected_table:
                    selected_columns.clear()
                    # Fetch columns for the selected table
                    cursor.execute(f"DESCRIBE {selected_table}")
                    columns = [row[0] for row in cursor.fetchall()]

                if columns:
                    selected_columns = request.GET.getlist('columns')

            context = {
                'databases': databases,
                'tables': tables,
                'columns': columns,
                'selected_database': selected_database,
                'selected_table': selected_table
            }

            # Redirect to the report generation page when columns are selected
            if selected_columns and databases and tables:
                return redirect('generate_report', database=selected_database, table=selected_table, columns=selected_columns)

            return render(request, 'QCA/select_database.html', context)
        
        except KeyError as e:
            context = {
            'wrong_db_message' : e
            }
            return render(request, 'QCA/select_database.html',context)

    
    
    #for other rdbms
    else:
        context = {
        'other_rdms_message' : "Other RDBMS are not available yet"
        }
        return render(request, 'QCA/credentials_form.html',context)

# View for generating the report
def generate_report(request, database, table, columns):
    # Get MySQL connection]
    try:
        conn = _get_mysql_connection(request)
        if not conn:
            return redirect('credentials_form')  # If no connection, redirect to credentials form

        cursor = conn.cursor()

        # Select the database
        cursor.execute(f"USE {database};")

        # Initialize an empty report dictionary
        report = {}

        #For testing
        # columns = columns = columns.split()
        # columns = ' '.join(columns)
        # columns = columns.split()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total_rows = cursor.fetchone()[0]

        columns = ast.literal_eval(columns)
        # Loop through the columns and calculate quality checks
        for column in columns:
                column_report = {}

                # 1. Null Value Count
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")
                column_report['null_count'] = cursor.fetchone()[0]

                # 2. Missing Value Count (Empty Strings)
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} = ''")
                column_report['missing_count'] = cursor.fetchone()[0]

                # 3. Duplicate Count
                # cursor.execute(f"SELECT COUNT(*) - COUNT(DISTINCT {column}) FROM {table}")
                # column_report['duplicate_count'] = cursor.fetchone()[0]

                # 4. Unique Values Count
                cursor.execute(f"SELECT COUNT(DISTINCT {column}) FROM {table}")
                column_report['unique_count'] = cursor.fetchone()[0]

                # # 5. Out-of-Range Values (for numeric columns, example: range 0-100)
                # cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} < 0 OR {column} > 100")
                # column_report['out_of_range'] = cursor.fetchone()[0]

                # 6. Age Validity Check (for "age" column)
                if column.lower() == 'age':
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} < 18 OR {column} > 100")
                    column_report['invalid_age'] = cursor.fetchone()[0]

                # 7. Positive Values Check (example: salary)
                if column.lower() == 'salary':  # You can customize this based on your column names
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} < 0")
                    column_report['negative_salary'] = cursor.fetchone()[0]

                # 7. Leading/Trailing Spaces (only for string columns)
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} REGEXP '^\\s|\\s$'")
                column_report['leading_trailing_spaces'] = cursor.fetchone()[0]

                # # 8. Invalid Email Format (if column is an email column)
                if column.lower() == 'email':
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} NOT REGEXP '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$'")
                    column_report['invalid_email'] = cursor.fetchone()[0]

                # 9. Length Check (only for string columns)
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE LENGTH({column}) > 100")  # Example: check length > 100
                column_report['long_values'] = cursor.fetchone()[0]

                # Calculate valid data percentage
                invalid_rows = column_report['null_count'] + column_report['missing_count']
                valid_rows = total_rows - invalid_rows
                column_report['valid_percentage'] = (valid_rows / total_rows) * 100

                # Add the column's quality check results to the report
                report[column] = column_report

        context = {
            'database': database,
            'table': table,
            'columns': columns,
            'report': report
        }

        #Testing
        print("-----------------------------------------------------",columns)
        print(context)
        return render(request, 'QCA/quality_check_report.html', context)
    
    except Exception as e:
        print("Error occur-", e)
