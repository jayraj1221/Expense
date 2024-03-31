from django.urls import path
from . import views



urlpatterns = [
    path('logout/', views.logout_user, name='logout'),
    path('',views.index,name="index"),
    path('register',views.register,name="register"),
    path('create_category',views.create_category,name="create_category"),
    path('category_list',views.category_list,name="category_list"),
    path('user_login',views.user_login,name="user_login"),
    path('category_dash',views.category_dash,name="category_dash"),
    path('category/update/<str:pk>/', views.category_update, name='category_update'),
    path('category/delete/<str:pk>/', views.category_delete, name='category_delete'),
    path('expense_dash',views.expense_dash,name="expense_dash"),
    path('add_expense',views.add_expense,name="add_expense" ),
    path('expense/edit/<int:pk>/', views.edit_expense, name='edit_expense'),  
    path('expense/delete/<int:pk>/', views.expense_delete, name='expense_delete'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('generate_graph/', views.generate_graph, name='generate_graph'),
    path('generate_pdf_report/', views.generate_pdf_report, name='generate_pdf_report'),
    path('demo_report/', views.demo_report, name='demo_report'),
]