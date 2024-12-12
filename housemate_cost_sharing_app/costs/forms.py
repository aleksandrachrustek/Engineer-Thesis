from django import forms
from .models import Task, Cost
from .groupmodel import CustomGroup
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'assigned_to', 'priority', 'progress']

    title = forms.CharField(required=True)
    description = forms.CharField(required=False)
    due_date = forms.DateField(required=True)

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super(TaskForm, self).__init__(*args, **kwargs)

        if group:
            self.fields['assigned_to'].queryset = group.users.all()

    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=True,
        label='Przydziel do',
        widget=forms.CheckboxSelectMultiple
    )
    
    priority_choices = [
        ('low', 'Niski'),
        ('medium', 'Średni'),
        ('high', 'Wysoki'),
    ]
    priority = forms.ChoiceField(choices=priority_choices, required=True, label='Priorytet')

    progress_choices = [
        ('not_started', 'Nie rozpoczęto'),
        ('in_progress', 'W trakcie'),
        ('completed', 'Zakończono'),
    ]
    progress = forms.ChoiceField(
        choices=progress_choices,
        required=True,
        label='Postęp',
    )  

class CostForm(forms.ModelForm):
    class Meta:
        model = Cost
        fields = ['name','amount', 'description', 'date','paid_by', 'paid_for', 'category']

    category_choices = [
    ('jedzenie', 'Jedzenie'),
    ('rachunki', 'Rachunki'),
    ('rozrywka', 'Rozrywka'),
    ('transport', 'Transport'),
    ('zdrowie', 'Zdrowie'),
    ('inne', 'Inne'),
    ]
    
    category = forms.ChoiceField(
        choices=category_choices,
        required=True,
        label='Kategoria',
    ) 
    name = forms.CharField(required=True)
    amount = forms.DecimalField(required=True)
    date = forms.DateField(required=True)
    description = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super(CostForm, self).__init__(*args, **kwargs)

        if group:
            self.fields['paid_by'].queryset = group.users.all()
            self.fields['paid_for'].queryset = group.users.all()

    paid_by = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=True,
        label='Zapłacone przez',
        widget=forms.CheckboxSelectMultiple
    )
    
    paid_for = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=True,
        label='Zapłacone za',
        widget=forms.CheckboxSelectMultiple
    )

    def clean(self):
        cleaned_data = super().clean()
        paid_for = cleaned_data.get('paid_for')
        paid_by = cleaned_data.get('paid_by')

        if not paid_by:
            raise forms.ValidationError('Musisz zaznaczyć, kto zapłacił.')

        if not paid_for:
            raise forms.ValidationError('Musisz zaznaczyć przynajmniej jednego użytkownika, za którego zapłacono.')

        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Hasło", 
        widget=forms.PasswordInput, 
        help_text="Hasło musi mieć przynajmniej 8 znaków."
    )
    password2 = forms.CharField(
        label="Powtórz hasło", 
        widget=forms.PasswordInput
    )
    username = forms.CharField(
        label="Nazwa użytkownika", 
    )
    email = forms.CharField(
        label="Adres email", 
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("To pole nie może być puste.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("To pole nie może być puste.")
        if '@' not in email:
            raise forms.ValidationError("Podany adres e-mail jest nie zawiera @.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Hasła muszą być takie same.")

        return cleaned_data