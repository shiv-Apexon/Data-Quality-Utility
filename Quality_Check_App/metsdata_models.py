from django.db import models

# Create your models here.
class ConnectionInfo(models.Model):
    conn_id = models.AutoField(primary_key=True)
    connection_name = models.CharField(max_length=255)
    platform = models.CharField(max_length=100)
    host = models.CharField(max_length=255)
    user = models.CharField(max_length=255)
    port = models.IntegerField()
    password = models.CharField(max_length=255)
    db_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'connection_info'
        managed = False
