from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('costslist/<int:group_id>/addcost/', views.add_cost, name='add_cost'),
    path('costslist/<int:group_id>/', views.costs_list, name='costs_list'),
    path('costslist/<int:group_id>/editcost/<int:cost_id>/', views.edit_cost, name='edit_cost'),
    path('costslist/<int:group_id>/deletecost/<int:cost_id>/', views.delete_cost, name='delete_cost'),
    path('taskslist/<int:group_id>/addtask/', views.add_task, name='add_task'),
    path('taskslist/<int:group_id>/', views.task_list, name='task_list'), 
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/join/', views.join_group, name='join_group'),
    path('groups/<int:group_id>/groupinfo/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/edit_group/', views.edit_group, name='edit_group'),
    path('groups/<int:group_id>/delete_group/', views.delete_group, name='delete_group'),
    path('taskslist/<int:group_id>/edittask/<int:task_id>/', views.edit_task, name='edit_task'),
    path('taskslist/<int:group_id>/deletetask/<int:task_id>/', views.delete_task, name='delete_task'),
    path('costslist/<int:group_id>/costdetail/<int:cost_id>/', views.cost_detail, name='cost_detail'),
    path('taskslist/<int:group_id>/taskdetail/<int:task_id>/', views.task_detail, name='task_detail'),
    path('groups/<int:group_id>/balance/', views.balance_view, name='balance_view'),
    path('group/<int:group_id>/statistics/', views.statistics_view, name='statistics'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('groups/<int:group_id>/settlement/', views.settlement_view, name='settlement_view')
]
