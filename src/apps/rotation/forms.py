from django import forms
from apps.dashboard.models import TaskList, Maintenance, WEEKDAY_FLAGS
from apps.user.models import Users

class TaskListForm(forms.ModelForm):
    #ビットフラグの複数選択を実現するためのフィールド
    frequency = forms.MultipleChoiceField(
        label="頻度(曜日)",
        choices=[(str(bit), label) for bit, label in WEEKDAY_FLAGS],
        widget=forms.CheckboxSelectMultiple,
    )
    #担当者の複数選択
    homemakers = forms.ModelMultipleChoiceField(
        label="担当者",
        queryset=Users.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    #重みの選択
    weight = forms.ChoiceField(
        label="重み",
        choices=[(str(i), str(i)) for i in range(1, 6)],
        help_text="1=簡単, 5=大変",
    )

    class Meta:
        model = TaskList
        fields = ["task_name", "frequency", "homemakers", "weight"]
        labels = {
            "task_name": "家事名",
        }

    def __init__(self, *args, **kwargs):
        login_user = kwargs.pop('login_user', None)
        super().__init__(*args, **kwargs)
        if login_user and getattr(login_user, 'household', None):
            qs = Users.objects.filter(household=login_user.household)
        else:
            qs = Users.objects.none()
        self.fields["homemakers"].queryset = qs
        if self.instance.pk:
            if self.instance.frequency:
                value = self.instance.frequency
                initial = []
                for bit, label in WEEKDAY_FLAGS:
                    if value & bit:
                        initial.append(str(bit))
                self.fields['frequency'].initial = initial
            self.fields["homemakers"].initial = self.instance.homemakers.all()

    def clean_frequency(self):
        selected = self.cleaned_data['frequency']
        total = 0
        for v in selected:
            total += int(v)
        return total

    def clean_weight(self):
        return int(self.cleaned_data['weight'])

class MaintenanceForm(forms.ModelForm):
    homemakers = forms.ModelMultipleChoiceField(
        label="担当者",
        queryset=Users.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,    #担当者をチェックボックスで選択
    )

    class Meta:
        model = Maintenance
        fields = ["target_name", "homemakers", "last_date", "next_date", "is_choice"]
        labels = {
            "target_name": "メンテナンス名",
            "last_date": "前回実施日",
            "next_date": "次回予定日",
            "is_choice": "選択式",
        }
        widgets={
            'last_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'next_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        login_user = kwargs.pop('login_user', None)
        super().__init__(*args, **kwargs)
        if login_user and getattr(login_user, 'household', None):
            qs = Users.objects.filter(household=login_user.household)
        else:
            qs = Users.objects.none()
        self.fields["homemakers"].queryset = qs
        if self.instance.pk:
            self.fields["homemakers"].initial = self.instance.homemakers.all()