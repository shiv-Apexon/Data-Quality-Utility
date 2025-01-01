from django.urls import path

from . import views

urlpatterns = [
    path("connect-db/", views.connect_db, name="connect-db"),
    path("dq_report_home/", views.dq_report_home, name="dq_report_home"),
    path("dataqualityhome/select_platform", views.select_platform, name="select_platform"),
    path("dataqualityhome/view_edit_connection", views.get_all_connections, name="get_all_connections"),
    path("dataqualityhome/db_info/", views.db_info, name="db_info"),
    path('get_tables/', views.get_tables, name='get_tables'),
    path('get_columns_and_types/', views.get_columns_and_types, name='get_columns_and_types'),
    path("dataqualityhome/", views.data_quality_home, name="data_quality_home"),
    path("", views.index, name="index"),
    path('close_connection/', views.close_connection, name='close_connection'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('save_column_details/', views.save_column_details, name='save_column_details'),
    path('save_quality_check_report/', views.save_quality_check_report, name='save_quality_check_report'),
    path('get_saved_details/', views.get_saved_details, name='get_saved_details'),
    path('get_conn_name/', views.get_conn_name, name='get_conn_name'),
    path('connect_db_with_conn_name/', views.connect_db_with_conn_name, name='connect_db_with_conn_name'),

    # Data Ingestion
    path('dataingestionhome/', views.data_ingestion_home, name='data_ingestion_home'),
    path("dataingestionhome/select_platform", views.select_platform, name="select_platform"),
    path("dataingestionhome/data_ingestion", views.data_ingestion, name="data_ingestion"),
]