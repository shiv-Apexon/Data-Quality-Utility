// static/js/form.js
$(document).ready(function () {
    // Show the modal immediately when the page loads
    $('#formModal').modal('show'); 

    // Load connections using AJAX
    loadConnections();

    // Load connections using AJAX
    function loadConnections() {
        $.ajax({
            url: '/get_conn_name/',  // Replace with your Django URL
            type: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'  // Add CSRF token for security
            },
            data: JSON.stringify( { platform: 'all' }),

            success: function (data) {
                var connSelect = $('#connection');
                connSelect.empty();
                connSelect.append('<option value="">--Select Connection--</option>');

                // Add connection options
                data.connections.forEach(function (conn) {
                    connSelect.append('<option value="' + conn + '">' + conn + '</option>');
                });

                // Enable the connection select dropdown
                connSelect.prop('disabled', false);
            },
            error: function () {
                alert('Error loading connections.');
            }
        });
    }
    // Handle connection selection change
    $('#connection').change(function () {
        var connName = $(this).val();
        if (connName) {
            $.ajax({
                url: '/connect_db_with_conn_name/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ conn_name: connName }),
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                success: function (response) {
                    alert('Connection details stored in session successfully.');
                },
                error: function (xhr, status, error) {
                    alert('Error storing connection details: ' + xhr.responseText);
                }
            });
        }
    });
    // Load databases based on selected connection
    $('#connection').change(function () {
        var connectionId = $(this).val();
        if (connectionId) {
            loadDatabases(connectionId);
        } else {
            $('#database').prop('disabled', true).empty().append('<option value="">--Select Database--</option>');
            $('#table').prop('disabled', true).empty().append('<option value="">--Select Table--</option>');
        }
    });

    // Load databases via AJAX
    function loadDatabases(connectionId) {
        $.ajax({
            url: '/get_databases/',  // Replace with your Django URL
            type: 'GET',
            data: { connection_id: connectionId },
            success: function (data) {
                var dbSelect = $('#database');
                dbSelect.empty();
                dbSelect.append('<option value="">--Select Database--</option>');

                // Add database options
                data.databases.forEach(function (db) {
                    dbSelect.append('<option value="' + db.id + '">' + db.name + '</option>');
                });

                dbSelect.prop('disabled', false);
            },
            error: function () {
                alert('Error loading databases.');
            }
        });
    }

    // Load tables based on selected database
    $('#database').change(function () {
        var databaseId = $(this).val();
        if (databaseId) {
            loadTables(databaseId);
        } else {
            $('#table').prop('disabled', true).empty().append('<option value="">--Select Table--</option>');
        }
    });

    // Load tables via AJAX
    function loadTables(databaseId) {
        $.ajax({
            url: '/get_tables/',  // Replace with your Django URL
            type: 'GET',
            data: { database_id: databaseId },
            success: function (data) {
                var tableSelect = $('#table');
                tableSelect.empty();
                tableSelect.append('<option value="">--Select Table--</option>');

                // Add table options
                data.tables.forEach(function (table) {
                    tableSelect.append('<option value="' + table.id + '">' + table.name + '</option>');
                });

                tableSelect.prop('disabled', false);
            },
            error: function () {
                alert('Error loading tables.');
            }
        });
    }

    // Handle form submission
    $('#connectionForm').submit(function (e) {
        e.preventDefault();

        var connection = $('#connection').val();
        var database = $('#database').val();
        var table = $('#table').val();

        // Send the data to the server via AJAX (POST request)
        $.ajax({
            url: '/submit_form/',  // Replace with your Django URL
            type: 'POST',
            data: {
                connection: connection,
                database: database,
                table: table,
                csrfmiddlewaretoken: '{{ csrf_token }}'  // CSRF token for security
            },
            success: function (response) {
                alert('Form submitted successfully!');
                $('#formModal').modal('hide');  // Close the modal after successful submission
            },
            error: function () {
                alert('Error submitting form.');
            }
        });
    });
});
