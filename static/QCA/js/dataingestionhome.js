document.getElementById('connector_div').addEventListener('click', function () {
    // Redirect to another HTML page within the same project
    window.location.href = 'select_platform?platform=data_ingestion';  // Replace 'next_page.html' with your target HTML file
});
document.getElementById('data_ingestion_div').addEventListener('click', function () {
    // Redirect to another HTML page within the same project
    window.location.href = 'data_ingestion';  // Replace 'next_page.html' with your target HTML file
});