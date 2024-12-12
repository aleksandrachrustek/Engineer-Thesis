from django.forms import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Cost, Task
from .models import CustomGroup
from .forms import TaskForm, CostForm, CustomUserCreationForm
from django.urls import reverse
from django.contrib.auth import get_user_model

class CostModelTest(TestCase):

    def setUp(self):
        # Tworzenie użytkownika i grupy do testów
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.group = CustomGroup.objects.create(name='Test Group')

    def test_create_cost(self):
        # Test tworzenia instancji Cost
        cost = Cost.objects.create(
            name='Zakup jedzenia',
            amount=50.00,
            description='Zakup jedzenia na kolację',
            date='2024-10-28',
            group=self.group
        )
        cost.paid_by.add(self.user1)
        cost.paid_for.add(self.user2)
        self.assertEqual(cost.name, 'Zakup jedzenia')
        self.assertEqual(cost.amount, 50.00)
        self.assertEqual(cost.paid_by.count(), 1)
        self.assertEqual(cost.paid_for.count(), 1)

    def test_cost_validation(self):
        # Test walidacji, aby upewnić się, że `paid_for` nie jest pusty
        cost = Cost(
            name='Zakup jedzenia',
            amount=50.00,
            description='Zakup jedzenia na kolację',
            date='2024-10-28',
            group=self.group,
        )

        cost.save()
        cost.paid_by.add(self.user1)
        with self.assertRaises(ValidationError):
            cost.clean()  


    def test_get_icon(self):
        # Test metody get_icon
        cost = Cost.objects.create(
            name='Zakup jedzenia',
            amount=50.00,
            description='Zakup jedzenia na kolację',
            date='2024-10-28',
            group=self.group,
            category='jedzenie'
        )
        self.assertEqual(cost.get_icon(), 'utensils')

class TaskModelTest(TestCase):

    def setUp(self):
        # Tworzenie użytkownika i grupy do testów
        self.user = User.objects.create_user(username='user', password='password')
        self.group = CustomGroup.objects.create(name='Test Group')

    def test_create_task(self):
        # Test tworzenia instancji Task
        task = Task.objects.create(
            title='Zadanie 1',
            description='Opis zadania 1',
            due_date='2024-10-30',
            group=self.group
        )
        task.assigned_to.add(self.user)
        self.assertEqual(task.title, 'Zadanie 1')
        self.assertEqual(task.assigned_to.count(), 1)

    def test_task_default_priority(self):
        # Test domyślnego priorytetu
        task = Task.objects.create(
            title='Zadanie 2',
            description='Opis zadania 2',
            due_date='2024-10-30',
            group=self.group
        )
        self.assertEqual(task.priority, 'medium')

    def test_task_progress_choices(self):
        # Test wyboru statusu
        task = Task.objects.create(
            title='Zadanie 3',
            description='Opis zadania 3',
            due_date='2024-10-30',
            group=self.group,
            progress='completed'
        )
        self.assertEqual(task.progress, 'completed')

class CustomGroupTest(TestCase):

    def setUp(self):
        # Tworzenie użytkownika dla testów
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_group_creation_without_code(self):
        # Test sprawdzający, czy kod jest generowany przy tworzeniu grupy
        group = CustomGroup.objects.create(name='Test Group')
        self.assertIsNotNone(group.code)
        self.assertEqual(len(group.code), CustomGroup.CODE_LENGTH)

    def test_group_creation_with_code(self):
        # Test sprawdzający, czy kod nie jest nadpisywany, gdy jest podany
        provided_code = 'ABC1234567'
        group = CustomGroup.objects.create(name='Test Group', code=provided_code)
        self.assertEqual(group.code, provided_code)

    def test_unique_code(self):
        # Test sprawdzający, czy kody są unikalne
        group1 = CustomGroup.objects.create(name='Group 1')
        group2 = CustomGroup.objects.create(name='Group 2')

        self.assertNotEqual(group1.code, group2.code)

    def test_code_length(self):
        # Test sprawdzający długość kodu
        group = CustomGroup.objects.create(name='Test Group')
        self.assertEqual(len(group.code), CustomGroup.CODE_LENGTH)

    def test_add_user_to_group(self):
        # Test sprawdzający, czy użytkownik może zostać dodany do grupy
        group = CustomGroup.objects.create(name='Test Group')
        group.users.add(self.user)

        self.assertIn(self.user, group.users.all())
        self.assertEqual(group.users.count(), 1)

class TaskFormTest(TestCase):

    def test_task_form_invalid_without_title(self):
        form_data = {
            'description': 'Description of the test task.',
            'due_date': '2024-10-30',
            'assigned_to': [],
            'priority': 'medium',
            'progress': 'not_started'
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

class CostFormTest(TestCase):

    def test_cost_form_invalid_without_paid_by(self):
        user = User.objects.create_user(username='testuser1', password='testpassword')
        form_data = {
            'name': 'Test Cost',
            'amount': 100.00,
            'description': 'Description of the test cost.',
            'date': '2024-10-30',
            'paid_for': [user.pk],
            'category': 'jedzenie'
        }
        form = CostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('paid_by', form.errors)

    def test_cost_form_invalid_without_paid_for(self):
        user = User.objects.create_user(username='testuser1', password='testpassword')
        form_data = {
            'name': 'Test Cost',
            'amount': 100.00,
            'description': 'Description of the test cost.',
            'date': '2024-10-30',
            'paid_by': [user.pk],
            'category': 'jedzenie'
        }
        form = CostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('paid_for', form.errors)

class CustomUserCreationFormTest(TestCase):

    def setUp(self):
        User.objects.all().delete()

    def test_user_creation_form_valid(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'H@fE!DQYe*O:z@LqsEZrp4P',
            'password2': 'H@fE!DQYe*O:z@LqsEZrp4P'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_user_creation_form_invalid_duplicate_username(self):
        User.objects.create_user(username='duplicateuser', password='password123', email='duplicate@example.com')
        form_data = {
            'username': 'duplicateuser',
            'email': 'test@example.com',
            'password1': 'H@fE!DQYe*O:z@LqsEZrp4P',
            'password2': 'H@fE!DQYe*O:z@LqsEZrp4P'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

class URLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = CustomGroup.objects.create(name='Test Group')
        self.client.login(username='testuser', password='testpassword')

    def test_index_url(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_costs_list_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('costs_list', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)

    def test_add_cost_url(self):
        response = self.client.get(reverse('add_cost', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)

    def test_edit_cost_url(self):
        cost = Cost.objects.create(name='Test Cost', amount=10.0, group=self.group, date='2024-10-28')
        response = self.client.get(reverse('edit_cost', args=[self.group.id, cost.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_cost_url(self):
        cost = Cost.objects.create(name='Test Cost', amount=10.0, group=self.group, date='2024-10-28')
        response = self.client.get(reverse('delete_cost', args=[self.group.id, cost.id]))
        self.assertEqual(response.status_code, 200)

    def test_add_task_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('add_task', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)

    def test_task_list_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('task_list', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)

    def test_register_url(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_url(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_group_list_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('group_list'))
        self.assertEqual(response.status_code, 200)

    def test_create_group_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('create_group'))
        self.assertEqual(response.status_code, 200)

    def test_join_group_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('join_group'))
        self.assertEqual(response.status_code, 200)

    def test_group_detail_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('group_detail', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)

    def test_edit_group_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('edit_group', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_group_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('delete_group', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)

    def test_balance_view_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('balance_view', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)

    def test_statistics_view_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('statistics', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)

    def test_settlement_view_url(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('settlement_view', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)

    def test_logout_url(self):
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        
User = get_user_model()

class ViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.group = CustomGroup.objects.create(name='Test Group')
        self.group.users.add(self.user)

        self.client.login(username='testuser', password='password123')

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'costs/index.html')

    def test_costs_list_view(self):
        response = self.client.get(reverse('costs_list', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'costs/costs_list.html')

    def test_delete_cost_view(self):
        cost = Cost.objects.create(
            name='Test Cost',
            amount=50.00,
            description='Some cost',
            date = '2024-12-31',
            group=self.group
        )
        response = self.client.post(reverse('delete_cost', args=[self.group.id, cost.id]))
        self.assertRedirects(response, reverse('costs_list', args=[self.group.id]))
        self.assertEqual(Cost.objects.count(), 0)

    def test_create_group_view(self):
        response = self.client.post(reverse('create_group'), {
            'group_name': 'New Group'
        })
        self.assertContains(response, 'New Group')
        self.assertEqual(CustomGroup.objects.count(), 2)

    def test_join_group_view(self):
        new_group = CustomGroup.objects.create(name='Joinable Group', code='join123')
        response = self.client.post(reverse('join_group'), {
            'group_code': 'join123'
        })
        self.assertRedirects(response, reverse('group_list'))
        self.assertIn(self.user, new_group.users.all())

    def test_group_list_view(self):
        response = self.client.get(reverse('group_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'costs/group_list.html')
    
    def test_edit_group_view(self):
        response = self.client.post(reverse('edit_group', args=[self.group.id]), {
            'name': 'Updated Group Name'
        })
        self.assertRedirects(response, reverse('group_detail', args=[self.group.id]))
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'Updated Group Name')

    def test_delete_group_view(self):
        group_to_delete = CustomGroup.objects.create(name='Group to Delete')
        response = self.client.post(reverse('delete_group', args=[group_to_delete.id]))
        self.assertRedirects(response, reverse('group_list'))
        self.assertEqual(CustomGroup.objects.count(), 1)

    def test_task_detail_view(self):
        task = Task.objects.create(
            title='Sample Task',
            description='Task description',
            due_date='2024-12-31',
            group=self.group
        )
        task.assigned_to.set([self.user.id])
        response = self.client.get(reverse('task_detail', args=[self.group.id, task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'costs/task_detail.html')

    def test_balance_view(self):
        response = self.client.get(reverse('balance_view', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'costs/balance.html')

    def test_statistics_view(self):
        response = self.client.get(reverse('statistics', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'costs/statistics.html')