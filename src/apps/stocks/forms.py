from django import forms
from .models import StockItem

class StockForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ['category', 'stock_name', 'quantity', 'period_days', 'purchase_date']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'category': 'カテゴリ',
            'stock_name': '在庫名',
            'quantity': '補充個数',
            'period_days': '消耗の目安',
            'purchase_date': '購入日',
        }
        