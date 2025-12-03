from django import forms
from .models import MaintenanceItem, FREQ_CHOICES

TYPE_CHOICES = (
    (True, '家電'),
    (False, '設備'),
)

class MaintenanceCreateForm(forms.ModelForm):
    is_appliance = forms.ChoiceField(
        label='区分', choices=TYPE_CHOICES, widget=forms.Select, initial=True
    )
    frequency = forms.ChoiceField(label='頻度', choices=FREQ_CHOICES)
    last_date = forms.DateField(label='最後に実施した日', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = MaintenanceItem
        fields = ['is_appliance', 'target_name', 'frequency', 'last_date']
        labels = {
            'target_name': '名称（家電名 / 設備名）',
        }

class MaintenanceDeleteForm(forms.Form):
    item_id = forms.IntegerField(widget=forms.Select)
    