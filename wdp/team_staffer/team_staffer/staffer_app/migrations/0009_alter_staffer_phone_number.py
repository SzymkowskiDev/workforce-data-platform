# Generated by Django 4.1.7 on 2023-04-05 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffer_app', '0008_staffer_last_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffer',
            name='phone_number',
            field=models.CharField(default='', max_length=100),
        ),
    ]