# Generated by Django 5.0.5 on 2024-10-14 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0003_cost_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cost',
            name='category',
            field=models.CharField(choices=[('food', 'Jedzenie'), ('utilities', 'Rachunki'), ('entertainment', 'Rozrywka'), ('transportation', 'Transport'), ('health', 'Zdrowie'), ('other', 'Inne')], default='other', max_length=15),
        ),
    ]
