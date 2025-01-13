from django.urls import path

from . import views as data_quality_views

urlpatterns = [
    path("connect-db/", data_quality_views.connect_db, name="connect-db"),
    path("dq_report_home/", data_quality_views.dq_report_home, name="dq_report_home"),
    path("dataqualityhome/select_platform", data_quality_views.select_platform, name="select_platform"),
    path("dataqualityhome/view_edit_connection", data_quality_views.get_all_connections, name="get_all_connections"),
    path("dataqualityhome/db_info/", data_quality_views.db_info, name="db_info"),
    path("dataqualityhome/", data_quality_views.data_quality_home, name="data_quality_home"),
    path("", data_quality_views.index, name="index"),
    path('close_connection/', data_quality_views.close_connection, name='close_connection'),
    path('generate_report/', data_quality_views.generate_report, name='generate_report'),

    # API's 
    path('get_conn_name/', data_quality_views.get_conn_name, name='get_conn_name'),
    path('get_saved_details/', data_quality_views.get_saved_details, name='get_saved_details'),
    path('connect_db_with_conn_name/', data_quality_views.connect_db_with_conn_name, name='connect_db_with_conn_name'),
    path('get_tables/', data_quality_views.get_tables, name='get_tables'),
    path('get_columns_and_types/', data_quality_views.get_columns_and_types, name='get_columns_and_types'),
    path('save_column_details/', data_quality_views.save_column_details, name='save_column_details'),
    path('save_quality_check_report/', data_quality_views.save_quality_check_report, name='save_quality_check_report'),
]