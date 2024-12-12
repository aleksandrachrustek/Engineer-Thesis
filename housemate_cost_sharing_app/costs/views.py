from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Cost
from .groupmodel import CustomGroup
from .forms import TaskForm, CostForm, CustomUserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField, Sum
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
import base64
import numpy as np
import pandas as pd
from datetime import datetime


def index(request):
    return render(request, 'costs/index.html')

@login_required
def task_list(request, group_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    assigned_user_id = request.GET.get('assigned_user')
    sort_order = request.GET.get('sort_order', 'due_date_asc')

    tasks = Task.objects.filter(group=group).annotate(
        priority_order=Case(
            When(priority='high', then=Value(1)),
            When(priority='medium', then=Value(2)),
            When(priority='low', then=Value(3)),
            output_field=IntegerField(),
        )
    ).order_by(
        'priority_order' if sort_order == 'default' else ('due_date' if 'asc' in sort_order else '-due_date')
    )

    if assigned_user_id:
        tasks = tasks.filter(assigned_to__id=assigned_user_id)

    users = group.users.all() 
    context = {
        'group_id': group_id,
        'tasks': tasks,
        'users': users,
        'sort_order': sort_order,
    }
    return render(request, 'costs/task_list.html', context)

@login_required
def add_task(request, group_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, group=group)
        if form.is_valid():
            task_instance = form.save(commit=False)
            task_instance.group = group
            task_instance.save()
            assigned_to_users = form.cleaned_data.get('assigned_to')
            if not assigned_to_users:
                form.add_error('assigned_to', 'Musisz zaznaczyć przynajmniej jednego użytkownika, aby przypisać zadanie.')
            else:
                task_instance.assigned_to.set(assigned_to_users)
                return redirect('task_list', group_id=group_id)
    else:
        form = TaskForm(group=group)
    return render(request, 'costs/add_task.html', {'form': form, 'group_id': group_id})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    members = group.users.all()
    return render(request, 'costs/group_detail.html', {'group': group, 'members': members, 'group_id': group_id})

@login_required
def add_cost(request, group_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    if request.method == 'POST':
        form = CostForm(request.POST, group=group)
        if form.is_valid():
            cost_instance = form.save(commit=False)
            cost_instance.group = group
            cost_instance.save()
            paid_by_users = form.cleaned_data.get('paid_by')
            paid_for_users = form.cleaned_data.get('paid_for')
            if not paid_by_users:
                form.add_error('paid_by', 'Musisz zaznaczyć przynajmniej jednego użytkownika, aby przypisać koszt.')
            else:
                cost_instance.paid_by.set(paid_by_users)
                if paid_for_users:
                    cost_instance.paid_for.set(paid_for_users)
                return redirect('costs_list', group_id=group_id)
    else:
        form = CostForm(group=group)
    return render(request, 'costs/add_cost.html', {'form': form, 'group_id': group_id})

@login_required
def costs_list(request, group_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    costs = Cost.objects.filter(group=group)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_date_obj > end_date_obj:
                messages.error(request, 'Data początkowa nie może być późniejsza niż data końcowa.')
            else:
                costs = costs.filter(date__range=[start_date, end_date])
        except ValueError:
            messages.error(request, 'Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD.')

    return render(request, 'costs/costs_list.html', {'costs': costs, 'group_id': group_id})

@login_required
def edit_cost(request, group_id, cost_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    cost = get_object_or_404(Cost, id=cost_id)
    if request.method == 'POST':
        form = CostForm(request.POST, instance=cost, group=group)
        if form.is_valid():
            form.save()
            return redirect('costs_list', group_id=cost.group.id)
    else:
        form = CostForm(instance=cost, group=group)
    return render(request, 'costs/edit_cost.html', {'form': form, 'cost': cost, 'group_id': group_id})

@login_required
def delete_cost(request, group_id, cost_id):
    cost = get_object_or_404(Cost, id=cost_id)
    if request.method == 'POST':
        cost.delete()
        return redirect('costs_list', group_id=group_id)
    return render(request, 'costs/delete_cost.html', {'cost': cost, 'group_id': group_id})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('group_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'costs/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('group_list')
        else:
            messages.error(request, "Nieprawidłowa nazwa użytkownika lub hasło.")
    return render(request, 'costs/login.html')

@login_required
def create_group(request):
    if request.method == "POST":
        group_name = request.POST.get("group_name")
        if group_name: 
            group = CustomGroup.objects.create(name=group_name)
            group.users.add(request.user)
            return render(request, 'costs/group_created.html', {'group': group}) 
        else:
            return render(request, 'costs/create_group.html', {'error': 'Group name is required'})
    return render(request, 'costs/create_group.html')

@login_required
def join_group(request):
    if request.method == "POST":
        group_code = request.POST.get("group_code")
        try:
            group = CustomGroup.objects.get(code=group_code)
            group.users.add(request.user)
            return redirect('group_list')
        except CustomGroup.DoesNotExist:
            return render(request, 'costs/join_group.html', {'error': 'Kod grupy nie istnieje. \n Proszę spróbować ponownie.'})
    return render(request, 'costs/join_group.html')

@login_required
def group_list(request):
    user_groups = request.user.user_groups.all()
    return render(request, 'costs/group_list.html', {'groups': user_groups})

@login_required
def edit_group(request, group_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    if request.method == 'POST':
        new_name = request.POST.get('name', group.name) 
        group.name = new_name 
        group.save()  
        return redirect('group_detail', group_id=group.id)  
    return render(request, 'costs/edit_group.html', {'group': group})

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list') 
    return render(request, 'costs/delete_group.html', {'group': group})

@login_required
def edit_task(request, group_id, task_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, group=group)
        if form.is_valid():
            form.save()
            return redirect('task_list', group_id=group_id)
    else:
        form = TaskForm(instance=task, group=group)
    return render(request, 'costs/edit_task.html', {'form': form,'group_id': group_id, 'task_id': task_id})

@login_required
def delete_task(request, group_id, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list', group_id=group_id)
    return render(request, 'costs/delete_task.html', {'group_id': group_id, 'task_id': task_id})

@login_required
def cost_detail(request, group_id, cost_id):
    cost = get_object_or_404(Cost, id=cost_id, group_id=group_id)
    return render(request, 'costs/cost_detail.html', {'cost': cost, 'group_id': group_id, 'cost_id': cost_id})

@login_required
def task_detail(request, group_id, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'costs/task_detail.html', {'task': task, 'group_id': group_id, 'task_id': task_id})


@login_required
def balance_view(request, group_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    users = group.users.all()
    if users.count() <= 1:
        return render(request, 'costs/balance.html', {
            'group_id': group_id,
        })
    balance_data = {user.id: {'user': user, 'total_paid': 0, 'total_owed': 0, 'balance': 0} for user in users}
    costs = Cost.objects.filter(group=group)

    for cost in costs:
        amount_per_person = cost.amount / cost.paid_for.count() if cost.paid_for.count() > 0 else 0
        for payer in cost.paid_by.all():
            balance_data[payer.id]['total_paid'] += cost.amount
            balance_data[payer.id]['balance'] -= amount_per_person 
        for receiver in cost.paid_for.all():
            if receiver not in cost.paid_by.all(): 
                balance_data[receiver.id]['total_owed'] += amount_per_person
                balance_data[receiver.id]['balance'] += amount_per_person 

    settlements = []
    debtors = []
    creditors = []
    
    for user_id, data in balance_data.items():
        if data['balance'] < 0: 
            debtors.append({'user': data['user'], 'amount': -data['balance']}) 
        elif data['balance'] > 0:  
            creditors.append({'user': data['user'], 'amount': data['balance']})

    for debtor in debtors:
        for creditor in creditors:
            if debtor['amount'] <= 0:
                break 
            amount_to_settle = min(debtor['amount'], creditor['amount']) 
            settlements.append({
                'debtor': creditor['user'],  
                'creditor': debtor['user'],  
                'amount': amount_to_settle
            })
            debtor['amount'] -= amount_to_settle
            creditor['amount'] -= amount_to_settle

    return render(request, 'costs/balance.html', {
        'balance_data': balance_data,
        'settlements': settlements,
        'group_id': group_id,
    })

@login_required
def statistics_view(request, group_id):
    months = [
        (1, 'Styczeń'), (2, 'Luty'), (3, 'Marzec'), (4, 'Kwiecień'),
        (5, 'Maj'), (6, 'Czerwiec'), (7, 'Lipiec'), (8, 'Sierpień'),
        (9, 'Wrzesień'), (10, 'Październik'), (11, 'Listopad'), (12, 'Grudzień')
    ]
    available_years = Cost.objects.filter(group_id=group_id).dates('date', 'year')
    years = [year.year for year in available_years] if available_years else list(range(datetime.now().year - 5, datetime.now().year + 1))
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_month = request.GET.get('month', None)
    costs = Cost.objects.filter(group_id=group_id, date__year=selected_year)
    if selected_month:
        costs = costs.filter(date__month=int(selected_month))
    if not costs.exists():
        return render(request, 'costs/statistics.html', {
            'group_id': group_id,
            'no_data': True,
            'selected_year': selected_year,
            'selected_month': int(selected_month) if selected_month else None,
            'months': months,
            'years': years
        })
    
    data = {}
    for cost in costs:
        users = cost.paid_by.all() 
        for user in users:
            if user.username not in data:
                data[user.username] = {}
            if cost.category not in data[user.username]:
                data[user.username][cost.category] = 0
            data[user.username][cost.category] += cost.amount
    users = list(data.keys())
    categories = sorted(set(cat for user_data in data.values() for cat in user_data.keys()))
    bar_height = np.zeros((len(users), len(categories)))
    for i, user in enumerate(users):
        for j, category in enumerate(categories):
            bar_height[i, j] = data[user].get(category, 0)
    fig, ax = plt.subplots(figsize=(10, 6))
    width = 0.15
    colors = ['pink', 'purple', 'lightblue', 'salmon', 'lightgreen']
    for i, user in enumerate(users):
        ax.bar(np.arange(len(categories)) + (i * width), bar_height[i], width, label=user, color=colors[i % len(colors)])
    ax.set_ylabel('Kwota (zł)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Kategorie', fontsize=14, fontweight='bold')
    ax.set_xticks(np.arange(len(categories)) + width * (len(users) - 1) / 2)
    ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=14)
    ax.legend()
    fig.patch.set_facecolor('#fff7f4')
    ax.set_facecolor('#fff7f4')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str_1 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)

    # Wykres 2: Wydatki całkowite według użytkownika
    total_costs_by_user = {user: sum(data[user].values()) for user in users}
    fig, ax = plt.subplots(figsize=(14, 14))
    ax.bar(total_costs_by_user.keys(), total_costs_by_user.values(), color='skyblue')
    ax.set_ylabel('Kwota (zł)', fontsize=30, fontweight='bold') 
    ax.set_xlabel('Użytkownik', fontsize=30, fontweight='bold') 
    ax.tick_params(axis='y', labelsize=28)  
    ax.tick_params(axis='x', labelsize=28) 
    fig.patch.set_facecolor('#fff7f4')
    ax.set_facecolor('#fff7f4')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str_2 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)

    # Wykres 3: Wydatki według kategorii (łącznie)
    total_costs_by_category = costs.values('category').annotate(total_amount=Sum('amount'))
    if total_costs_by_category:
        categories, total_amounts = zip(*[(item['category'], item['total_amount']) for item in total_costs_by_category])
    else:
        categories, total_amounts = [], []
    fig, ax = plt.subplots(figsize=(14, 14))
    ax.bar(categories, total_amounts, color='lightgreen')
    ax.set_ylabel('Kwota (zł)', fontsize=30, fontweight='bold') 
    ax.set_xlabel('Kategorie', fontsize=30, fontweight='bold')
    ax.tick_params(axis='y', labelsize=28) 
    ax.tick_params(axis='x', labelsize=28)  
    fig.patch.set_facecolor('#fff7f4')
    ax.set_facecolor('#fff7f4')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    ax.set_xticks(np.arange(len(categories))) 
    ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=28)
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str_3 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)

    # Wykres 4: Wydatki w czasie (trend wydatków w czasie)
    costs_df = pd.DataFrame(list(costs.values('date', 'amount')))
    img_str_4 = None  
    if 'date' in costs_df.columns and not costs_df['date'].isnull().all():
        costs_df['date'] = pd.to_datetime(costs_df['date']).dt.date
        time_series = costs_df.groupby('date').sum().reset_index()
        if not time_series.empty:
            fig, ax = plt.subplots(figsize=(14, 10))
            ax.plot(time_series['date'], time_series['amount'], marker='o', color='purple')
            ax.set_ylabel('Kwota (zł)', fontsize=18, fontweight='bold') 
            ax.set_xlabel('Data', fontsize=18, fontweight='bold') 
            ax.tick_params(axis='y', labelsize=16)  
            ax.tick_params(axis='x', labelsize=16)  
            fig.patch.set_facecolor('#fff7f4')
            ax.set_facecolor('#fff7f4')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
            buffer = BytesIO()
            plt.tight_layout()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            img_str_4 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close(fig)

    # Wykres 5: Udział procentowy wydatków według kategorii
    if total_costs_by_category:
        fig, ax = plt.subplots(figsize=(14, 14))
        ax.pie(total_amounts, labels=categories, autopct='%1.1f%%', colors=colors, startangle=0, textprops={'fontsize': 34})
        ax.axis('equal') 
        fig.patch.set_facecolor('#fff7f4')
        ax.set_facecolor('#fff7f4')
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        img_str_5 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)

    # Wykres 6: Udział procentowy wydatków według użytkownika (Pie Chart)
    fig, ax = plt.subplots(figsize=(14, 14))
    ax.pie(total_costs_by_user.values(), labels=total_costs_by_user.keys(), autopct='%1.1f%%', colors=colors, startangle=90, textprops={'fontsize': 34})  
    ax.axis('equal')  
    fig.patch.set_facecolor('#fff7f4')
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str_6 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)

    return render(request, 'costs/statistics.html', {
        'group_id': group_id,
        'img_str_1': img_str_1,
        'img_str_2': img_str_2,
        'img_str_3': img_str_3,
        'img_str_4': img_str_4,
        'img_str_5': img_str_5,
        'img_str_6': img_str_6,
        'months': months,
        'years': years,
        'selected_year': selected_year,
        'selected_month': int(selected_month) if selected_month else None,
    })

@login_required
def settlement_view(request, group_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    user_id = request.GET.get('user_id')
    month = request.GET.get('month')
    year = request.GET.get('year')
    expenses = Cost.objects.filter(group=group)

    if user_id:
        expenses = expenses.filter(paid_by__id=int(user_id))  
    if month:
        expenses = expenses.filter(date__month=int(month)) 
    if year:
        expenses = expenses.filter(date__year=int(year)) 

    category_sums = expenses.values('category').annotate(total=Sum('amount')).order_by('category')
    total_sum = expenses.aggregate(total=Sum('amount'))['total'] or 0 
    users = group.users.all()
    available_years = expenses.dates('date', 'year').distinct()
    available_months = [
        (1, 'Styczeń'), (2, 'Luty'), (3, 'Marzec'), (4, 'Kwiecień'),
        (5, 'Maj'), (6, 'Czerwiec'), (7, 'Lipiec'), (8, 'Sierpień'),
        (9, 'Wrzesień'), (10, 'Październik'), (11, 'Listopad'), (12, 'Grudzień')
    ]

    return render(request, 'costs/settlement_view.html', {
        'group_id': group_id,
        'category_sums': category_sums,
        'users': users,
        'available_years': available_years,
        'available_months': available_months,
        'total_sum': total_sum,  
    })