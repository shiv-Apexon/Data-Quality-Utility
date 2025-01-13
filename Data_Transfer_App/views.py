from django.shortcuts import render,redirect
from django.http import HttpResponse

def data_ingestion_home(request):
    """
    Description:
      This function renders the data ingestion home page.
    Parameters:
      request (HttpRequest): The HTTP request object.
    Returns:
      HttpResponse: The rendered HTML response for the data ingestion home page.
    """
    return render(request, 'data_transfer_app/dataingestionhome.html')

def data_ingestion(request):
    """
    Description:
      This function renders the data ingestion page.
    Parameters:
      request (HttpRequest): The HTTP request object.
    Returns:
      HttpResponse: The rendered HTML response for the data ingestion page.
    """
    return render(request, 'data_transfer_app/data_ingestion.html')

