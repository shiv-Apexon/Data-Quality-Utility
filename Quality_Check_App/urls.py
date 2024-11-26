from django.urls import path

from . import views

urlpatterns = [
    path("connect-db/", views.connect_db, name="connect-db"),
    path("db_info/", views.db_info, name="db_info"),
    path('get_tables/', views.get_tables, name='get_tables'),
    path('get_columns/', views.get_columns, name='get_columns'),
    path("", views.index, name="index"),
    path('close_connection/', views.close_connection, name='close_connection'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('save_column_details/', views.save_column_details, name='save_column_details'),

]