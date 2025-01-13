from django.urls import path

from . import views as data_transfer_views
from shared.views import views as shared_views

urlpatterns=[  
    # Data Ingestion
    path('dataingestionhome/', data_transfer_views.data_ingestion_home, name='data_ingestion_home'),
    path("dataingestionhome/data_ingestion", data_transfer_views.data_ingestion, name="data_ingestion"),

    # Shared
    path("dataingestionhome/select_platform", shared_views.select_platform, name="select_platform"),
    path('database_connection/', shared_views.database_connection, name='database_connection'),
]