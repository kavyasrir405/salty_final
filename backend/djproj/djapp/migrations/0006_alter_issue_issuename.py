# Generated by Django 4.2.2 on 2024-06-04 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djapp', '0005_alter_sprint_end_date_alter_sprint_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='IssueName',
            field=models.CharField(default='', max_length=30, unique=True),
        ),
    ]
