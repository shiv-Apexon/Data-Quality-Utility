from django.urls import path

from . import views

urlpatterns = [
    path("connect-db/", views.connect_db, name="connect-db"),
    path("db_info/", views.db_info, name="db_info"),
    path('get_tables/', views.get_tables, name='get_tables'),
    path('get_columns_and_types/', views.get_columns_and_types, name='get_columns_and_types'),
    path("", views.index, name="index"),
    path('close_connection/', views.close_connection, name='close_connection'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('save_column_details/', views.save_column_details, name='save_column_details'),
    path('save_quality_check_report/', views.save_quality_check_report, name='save_quality_check_report'),
    path('get_saved_details/', views.get_saved_details, name='get_saved_details'),


]