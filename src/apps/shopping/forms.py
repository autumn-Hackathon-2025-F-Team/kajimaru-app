from django import forms

class ShoppingAddForm(forms.Form):
    item_name = forms.CharField(label='商品名', max_length=20)
    quantity = forms.IntegerField(label='数量', min_value=1, initial=1)
    description = forms.CharField(label='説明', widget=forms.Textarea(attrs={'rows': 2}), required=False)