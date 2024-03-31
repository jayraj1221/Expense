# forms.py
from django import forms
from .models import Category,Expense

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'name', 'amount', 'description', 'date']
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)

class ExpenseFormUpdate(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'name', 'amount', 'description', 'date']