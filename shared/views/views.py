from django.shortcuts import render,redirect
from django.http import HttpResponse


# Shared views aross projects
def database_connection(request):
    platform = request.GET.get('platform')
    base_template = 'base_data_ingestion.html'
    return render(request, 'database_connection.html', {'platform': platform, 'base_template': base_template})

def select_platform(request):
    """
    Description:
      This function handles the selection of a platform from the request and renders the appropriate template.
    Parameters:
      request (HttpRequest): The HTTP request object containing GET parameters.
    Returns:
      HttpResponse: The rendered HTML response with the selected platform and base template.
    """
    
    platform = request.GET.get('platform', 'data_quality')  # It is temporary.

    base_template = 'base_data_ingestion.html'

    return render(request, 'select_platform.html', {'platform':platform,'base_template': base_template})