# Generated by Django 4.1.7 on 2023-04-01 18:13

from django.db import migrations
import phone_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('staffer_app', '0003_remove_staffer_avatar_delete_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffer',
            name='phone_number',
            field=phone_field.models.PhoneField(blank=True, help_text='Contact phone number', max_length=31),
        ),
    ]
