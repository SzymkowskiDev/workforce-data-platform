# Generated by Django 4.1.7 on 2023-03-30 19:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staffer_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('staffer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staffer_app.staffer')),
            ],
        ),
    ]
