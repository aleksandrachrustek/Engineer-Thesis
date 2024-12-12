# Generated by Django 5.0.5 on 2024-10-13 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='priority',
            field=models.CharField(choices=[('low', 'Niski'), ('medium', 'Średni'), ('high', 'Wysoki')], default='medium', max_length=10),
        ),
        migrations.AddField(
            model_name='task',
            name='progress',
            field=models.CharField(choices=[('not_started', 'Nie rozpoczęto'), ('in_progress', 'W trakcie'), ('completed', 'Zakończono')], default='not_started', max_length=15),
        ),
    ]
