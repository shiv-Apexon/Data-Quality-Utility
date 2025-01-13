# Generated by Django 5.1.3 on 2025-01-03 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConnectionInfo',
            fields=[
                ('conn_id', models.AutoField(primary_key=True, serialize=False)),
                ('connection_name', models.CharField(max_length=255)),
                ('platform', models.CharField(max_length=100)),
                ('host', models.CharField(max_length=255)),
                ('user', models.CharField(max_length=255)),
                ('port', models.IntegerField()),
                ('password', models.CharField(max_length=255)),
                ('db_name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'connection_info',
                'managed': False,
            },
        ),
    ]
