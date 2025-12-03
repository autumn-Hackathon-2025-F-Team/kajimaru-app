from django import forms
from .models import Task, Maintenance, TaskList, WEEKDAY_FLAGS
from apps.user.models import Users

#曜日選択
class TaskListForm(forms.ModelForm):
    frequency = forms.MultipleChoiceField(
        label="頻度(曜日)",
        choices=[(str(bit), label) for bit, label in WEEKDAY_FLAGS],
        widget=forms.CheckboxSelectMultiple,
        help_text="家事を行う曜日を選択してください。",
    )

#担当者選択
    homemakers = forms.ModelMultipleChoiceField(
        label="担当者",
        queryset=Users.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="家事の担当者を選択してください。",
    )

#重み
    weight = forms.ChoiceField(
        label="重み",
        choices=[(str(i), str(i)) for i in range(1, 6)],
        help_text="家事の重みを1(簡単)から5(大変)で選択してください。",
    )

    class Meta:
        model = TaskList
        fields = ['task_name', 'frequency', 'homemakers', 'weight']

# ログインユーザーの家族を担当者候補に設定
    def __init__(self, *args, login_user: Users = None, **kwargs):
        super().__init__(*args, **kwargs)
        if login_user and login_user.household:
            self.fields['homemakers'].queryset = Users.objects.filter(household=login_user.household)
        else:
            self.fields['homemakers'].queryset = Users.objects.none()

#ビットフラグに変換
    def clean_frequency(self):
        bits = self.cleaned_data.get('frequency', [])
        total = 0
        for bit_str in bits:
            total += int(bit_str)
        return total

    def clean_weight(self):
        weight_str = self.cleaned_data.get('weight')
        return int(weight_str) if weight_str is not None else None

class MaintenanceForm(forms.ModelForm):
    homemakers = forms.ModelMultipleChoiceField(
        label="担当者",
        queryset=Users.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

class Meta:
        model = Maintenance
        fields = ['target_name', 'homemakers', 'last_date', 'next_date', 'is_choice']

def __init__(self, *args, login_user: Users = None, **kwargs):
    super().__init__(*args, **kwargs)
    if login_user and login_user.household:
        self.fields['homemakers'].queryset = Users.objects.filter(household=login_user.household)
    else:
        self.fields['homemakers'].queryset = Users.objects.none()

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['substitute', 'is_completed', 'is_busy']