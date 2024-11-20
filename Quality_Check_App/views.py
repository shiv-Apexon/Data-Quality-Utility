from django.shortcuts import render, redirect
import mysql.connector
import ast

# View for the credentials form page
def credentials_form(request):
    if request.method == "POST":
        # Get credentials from the form
        hostname = request.POST.get('hostname')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Store the credentials in the session or elsewhere
        request.session['db_conn_details'] = {
            'hostname': hostname,
            'username': username,
            'password': password
        }
        # After the form is submitted, redirect to the select_database page
        return redirect('select_database')  # Correct redirect to select_database URL

    return render(request, 'QCA/credentials_form.html')  # Render the form if GET request

# View for selecting the database, table, and columns

def get_mysql_connection(request):
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
        return None

def select_database(request):
    # Get MySQL connection
    conn = get_mysql_connection(request)
    if not conn:
        return redirect('credentials_form')  # If no connection, redirect to credentials form

    cursor = conn.cursor()

    # Fetch the list of databases
    cursor.execute("SHOW DATABASES")
    databases = [row[0] for row in cursor.fetchall()]

    selected_database = request.GET.get('database')
    tables = []
    columns = []

    if selected_database:
        # Select the database
        cursor.execute(f"USE {selected_database};")

        # Fetch the list of tables
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]

        selected_table = request.GET.get('table')
        if selected_table:
            # Fetch columns for the selected table
            cursor.execute(f"DESCRIBE {selected_table}")
            columns = [row[0] for row in cursor.fetchall()]

    context = {
        'databases': databases,
        'tables': tables,
        'columns': columns,
        'selected_database': selected_database,
        'selected_table': request.GET.get('table'),
    }

    # Redirect to the report generation page when columns are selected
    if request.GET.getlist('columns'):
        return redirect('generate_report', database=selected_database, table=selected_table, columns=request.GET.getlist('columns'))

    return render(request, 'QCA/select_database.html', context)

# Example view for generating the report (for completeness)
def generate_report(request, database, table, columns):
    # Get MySQL connection
    conn = get_mysql_connection(request)
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

    columns = ast.literal_eval(columns)
    # Loop through the columns and calculate quality checks
    for column in columns:
        column = column.strip("'[],")
        if column:  # Ensure column is not empty
            try:
                # Count NULL values for the column
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")
                null_count = cursor.fetchone()[0]

                # Count missing values (empty strings or NULL)
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} = '' OR {column} IS NULL")
                missing_count = cursor.fetchone()[0]

                # Store the counts in the report dictionary
                report[column] = {
                    'null_count': null_count,
                    'missing_count': missing_count
                }
            except mysql.connector.Error as err:
                # If there's a MySQL error (invalid column, etc.), record the error for that column
                report[column] = {'error': f"SQL Error: {err}"}
    context = {
        'database': database,
        'table': table,
        'columns': columns,
        'report': report
    }
    print("-----------------------------------------------------",columns)
    print(context)
    return render(request, 'QCA/quality_check_report.html', context)