from django import forms
from .models import Users

REL_CHOICES = [('self', '本人'), ('spouse', '配偶者'), ('parent', '親'), ('child', '子'), ('other', 'その他')]

ROLE_CHOICES = [('admin', '管理者'), ('member', 'メンバー')]

AVATAR_CHOICES = [
    ('boy', '男の子'),
    ('girl', '女の子'),
    ('man', '男性'),
    ('woman', '女性'),
]

class AdminSignupForm(forms.Form):
    name = forms.CharField(label='名前', max_length=50)
    nickname = forms.CharField(label='ニックネーム', max_length=50, required=False)
    relation = forms.ChoiceField(choices=REL_CHOICES, initial='self', label='家族内での立場')
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='パスワード（確認用）', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix =''

class AdminLoginForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix =''

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
            'min_length': '招待コードは8桁で入力してください。',
            'max_length': '招待コードは8桁で入力してください。',
        },
    )

    def clean_code8(self):
        v = self.cleaned_data['code8']
        if not v.isdigit():
            raise forms.ValidationError('招待コードは8桁の数字で入力してください。')
        return v

class PinSetForm(forms.Form):
    pin1 = forms.CharField(
        label="PIN（4桁数字）",
        min_length=4, max_length=4,
        widget=forms.PasswordInput(attrs={"inputmode": "numeric", "autocomplete": "off"})
    )
    pin2 = forms.CharField(
        label="PIN（もう一度）",
        min_length=4, max_length=4,
        widget=forms.PasswordInput(attrs={"inputmode": "numeric", "autocomplete": "off"})
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('pin1', '')
        p2 = cleaned.get('pin2', '')
        if not (p1.isdigit() and p2.isdigit()):
            raise forms.ValidationError('PINは数字4桁で入力してください。')
        if p1 != p2:
            raise forms.ValidationError('確認用PINが一致しません。')
        return cleaned
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix =''


class PinVerifyForm(forms.Form):
    pin = forms.CharField(
        label='PIN（4桁数字）',
        min_length=4, max_length=4,
        widget=forms.PasswordInput(attrs={'inputmode': 'numeric', 'autocomplete': 'off'})
    )

    def clean_pin(self):
        v = self.cleaned_data['pin']
        if not v.isdigit():
            raise forms.ValidationError('PINコードは４桁の数字で入力してください。')
        return v
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''


class MemberForm(forms.ModelForm):
    display_name = forms.CharField(label='名前', max_length=50)
    nickname = forms.CharField(label='ニックネーム', max_length=50, required=False)
    relation_to_admin = forms.ChoiceField(label='家族内での立場', choices=REL_CHOICES, initial='other')
    role = forms.ChoiceField(label='権限', choices=ROLE_CHOICES, initial='member')
    avatar_key = forms.ChoiceField(
        label='アイコン',
        choices=AVATAR_CHOICES,
        required=False,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Users
        fields = ['display_name', 'nickname', 'relation_to_admin', 'role', 'avatar_key']

class AdminPinForm(forms.Form):
    pin = forms.CharField(
        label='PIN（4桁数字）',
        min_length=4, max_length=4,
        widget=forms.PasswordInput(attrs={'inputmode': 'numeric', 'autocomplete': 'one-time-code'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

class AvatarUpdateForm(forms.ModelForm):
    avatar_key = forms.ChoiceField(
        label='アイコン',
        choices=AVATAR_CHOICES,
        required=False,
        widget=forms.RadioSelect,
    )
    class Meta:
        model = Users
        fields = ['display_name', 'nickname', 'relation_to_admin', 'role', 'avatar_key']
