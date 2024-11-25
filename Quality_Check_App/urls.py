from django.urls import path

from . import views


urlpatterns = [
    # URL for Page 1 (Credentials Form)
    path('credentials/', views.credentials_form, name='credentials_form'),

    # URL for Page 2 (Select Database, Table, Columns)
    path('select-database/', views.select_database, name='select_database'),
    
    # URL for Page 3 (Quality Check Report)
    path('generate-report/<str:database>/<str:table>/<str:columns>/', views.generate_report, name='generate_report'),


]