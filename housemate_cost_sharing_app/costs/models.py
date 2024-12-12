from django.db import models
from django.contrib.auth.models import User
from .groupmodel import CustomGroup
from django.forms import ValidationError

class Task(models.Model):

    PRIORITY_CHOICES = [
        ('low', 'Niski'),
        ('medium', 'Średni'),
        ('high', 'Wysoki'),
    ]

    STATUS_CHOICES = [
        ('not_started', 'Nie rozpoczęto'),
        ('in_progress', 'W trakcie'),
        ('completed', 'Zakończono'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    assigned_to = models.ManyToManyField(User, related_name='assigned_tasks')
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    progress = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')


    def __str__(self):
        return self.title
    
class Cost(models.Model):

    CATEGORY_CHOICES = [
    ('jedzenie', 'Jedzenie'),
    ('rachunki', 'Rachunki'),
    ('rozrywka', 'Rozrywka'),
    ('transport', 'Transport'),
    ('zdrowie', 'Zdrowie'),
    ('inne', 'Inne'),
    ]

    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateField()
    paid_by = models.ManyToManyField(User, related_name='costs_paid')
    paid_for = models.ManyToManyField(User, related_name='costs_shared')
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='inne')

    def clean(self):
        if self.pk is not None: 
            if not self.paid_for.exists():
                raise ValidationError('Musisz wybrać przynajmniej jedną osobę, za którą zapłacono.')

    def __str__(self):
        return f"{self.description} - {self.amount}"

    def get_icon(self):
        icons = {
            'jedzenie': 'utensils',
            'rachunki': 'plug',
            'rozrywka': 'film',
            'transport': 'bus',
            'zdrowie': 'flask',
            'inne': 'gift',
        }
        return icons.get(self.category, 'question-circle')