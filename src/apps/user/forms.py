from django import forms

REL_CHOICES = [('self', '本人'), ('spouse', '配偶者'), ('parent', '親'), ('child', '子'), ('other', 'その他')]

ROLE_CHOICES = [('admin', '管理者'), ('member', 'メンバー')]

class AdminSignupForm(forms.Form):
    name = forms.CharField(label='名前', max_length=50)
    nickname = forms.CharField(label='ニックネーム', max_length=50, required=False)
    relation = forms.ChoiceField(choices=REL_CHOICES, initial='self', label='家族内での立場')
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='パスワード（確認用）', widget=forms.PasswordInput)

class AdminLoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)

class JoinCodeForm(forms.Form):
    code8 = forms.CharField(
        label = '参加コード（８桁）',
        min_length=8,
        max_length=8,
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',
            'pattern': r'\d{8}',
            'autocomplete': 'one-time-code',
            'placehoder': '12345678',
        }),
        error_messages={
            'min_length': '参加コードは8桁で入力してください。',
            'max_length': '参加コードは8桁で入力してください。',
        },
    )

    def clean_code8(self):
        v = self.cleaned_data['code8']
        if not v.isdigit():
            raise forms.ValidationError('参加コードは8桁の数字で入力してください。')
        return v

class PinForm(forms.Form):
    pin = forms.CharField(
        label='４桁のPINコード',
        min_length=4,
        max_length=4,
        widget=forms.PasswordInput(attrs={
            'inputmode': 'numeric',
            'pattern': r'\d{4}',
            'maxlength': '4',
            'placeholder': '••••',
        }),
        error_messages={
            'required': 'PINコードを入力してください',
            'min_length': 'PINコードは４桁です',
            'max_length': 'PINコードは４桁です',
        },   
    )

    def clean_pin(self):
        v = self.cleaned_data['pin']
        if not v.isdigit():
            raise forms.ValidationError('PINコードは４桁の数字で入力してください。')
        return v

class MemberForm(forms.Form):
    display_name = forms.CharField(label='名前', max_length=50)
    nickname = forms.CharField(label='ニックネーム', max_length=50, required=False)
    relation = forms.ChoiceField(label='家族内での立場', choices=REL_CHOICES, initial='other')
    role = forms.ChoiceField(label='権限', choices=ROLE_CHOICES, initial='member')
    avatar = forms.URLField(label='アイコンURL', required=False)