from django.shortcuts import render
from django.http.response import HttpResponse
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import Expense,Category
from .forms import CategoryForm,ExpenseForm,ExpenseFormUpdate
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
import pandas as pd
from decimal import Decimal
from django.db.models.functions import ExtractMonth
import matplotlib.pyplot as plt
from io import BytesIO
from django.db.models import Sum 
import base64
import json
# Create your views here.

def index(request):
    user = request.user
    expense_categories = Category.objects.all()
    total_expenses = 0
    recent_transactions = None
    if user.is_authenticated:
        user_expenses = Expense.objects.filter(user=user)
        total_expenses = user_expenses.aggregate(total_amount=Sum('amount'))['total_amount']
        recent_transactions = user_expenses.order_by('-date')[:5]
        if total_expenses is None:
            total_expenses = 0
    context = {
        'total_expenses': total_expenses,
        'recent_transactions': recent_transactions,
        'expense_categories': expense_categories,
    }
    return render(request, 'index.html', context)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(password)
        user = User.objects.create_user(username, email, password)
        login(request,user)
        return redirect('index')
    return render(request,'register.html')

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            existing_category = Category.objects.filter(name=name)
            if not existing_category:
                form.save()
                categories = Category.objects.all()
                return render(request,'category.html',{'categories': categories}) 
    else:
        form = CategoryForm()
    categories = Category.objects.all()
    return render(request,'category.html',{'categories': categories})
    

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(index)
        else:
            return render(request,'login.html')
    else:
        return render(request, 'login.html')
    
def category_dash(request):
    user = request.user
    categories = Category.objects.filter()
    return render(request,"category.html",{'categories': categories})

def category_update(request,pk):
    category = get_object_or_404(Category, name=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_dash')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'category_update.html', {'form': form})

def category_delete(request,pk):
    category = get_object_or_404(Category, name=pk)
    
    if request.method == 'POST':
            category.delete()
            return redirect('category_dash')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'category_delete.html', {'form': form})

def expense_dash(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(user=request.user)
    d = {'categories': categories,'expenses':expenses}
    return render(request, 'expense_dash.html',d)

def add_expense(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        user = request.user
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        category = Category.objects.get(name=request.POST.get('category'))
        Expense.objects.create(user=user,name=name,category=category,amount=amount,description=description,date=date)      
    return redirect('expense_dash')
    
def edit_expense(request,pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseFormUpdate(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_dash')
    else:
        form = ExpenseFormUpdate(instance=expense)
    return render(request,'expense_update.html',{'form':form})

    # return render(request, 'expense_update.html', {'form': form})
def expense_delete(request,pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        
        expense.delete()
        
        return redirect('expense_dash') 

    return redirect('expense_dash')
    return HttpResponse('hello')


def logout_user(request):
    logout(request)
    return redirect('index')

def generate_report(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        category = request.GET.get('category')
        expenses = Expense.objects.filter(user=request.user)
        categories = Category.objects.all()
        if start_date:
            expenses = expenses.filter(date__gte=start_date)
        if end_date:
            expenses = expenses.filter(date__lte=end_date)
        if category:
            if category != "all":
                expenses = expenses.filter(category__name=category)

        context = {
            'expenses': expenses,
            'categories':categories
        }
        return render(request, 'expense_report.html', context)
    else:
        return render(request, 'expense_report.html')

def generate_graph(request):
    expenses = Expense.objects.filter(user=request.user)
    data = {
        'Category': [expense.category.name for expense in expenses],
        'Amount': [expense.amount for expense in expenses]
    }
    df = pd.DataFrame(data)
    category_totals = df.groupby('Category')['Amount'].sum().reset_index()
    category_totals['Percentage'] = (category_totals['Amount'] / category_totals['Amount'].sum()) * 100
    plt.figure(figsize=(5, 6))
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
    num_categories = len(category_totals)
    explode = [0.1 if i == 0 else 0 for i in range(num_categories)]

    plt.pie(category_totals['Percentage'], labels=category_totals['Category'], autopct='%1.1f%%',
            colors=colors, explode=explode, shadow=True, startangle=140)
    plt.title('Expense Distribution by Category', fontsize=16)
    plt.axis('equal') 
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')
    plt.close()
    context = {'graphic': graphic}
    return render(request, 'graph.html', context)

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def generate_pdf_report(request):
    now = timezone.localtime(timezone.now())
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    template_path = 'your_template.html'  
    expenses = Expense.objects.filter(user=request.user)
    context = {'expenses': expenses,'total_expenses': len(expenses),'timestamp': timestamp} 
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expense_report.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')

    return response

def monthly_expense_data():
    data = Expense.objects.annotate(month=ExtractMonth('date')).values('month').annotate(total_amount=Sum('amount'))
    monthly_expense = {entry['month']: float(entry['total_amount']) for entry in data}  # Convert Decimal to float
    return json.dumps(monthly_expense)

def demo_report(request):
    monthly_data = monthly_expense_data()
    context = {'monthly_data': monthly_data}
    return render(request, 'demo_report.html', context)
