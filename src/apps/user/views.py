from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AdminSignupForm, JoinCodeForm, PinForm, AdminLoginForm
from django.utils.crypto import get_random_string
from .models import Household, Member, JoinCode
from django.utils import timezone
from django.db import transaction
from datetime import timedelta


HK = "household_id"
MK = 'active_member_id'
LS = 'profile_last_seen'


def _gen_household_name(email: str) -> str:
    return f"household-{email.split('@')[0]}-{get_random_string(6)}"

def signup(request):
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']; password = form.cleaned_data['password']
            name = form.cleaned_data['name']; nickname = form.cleaned_data['nickname', '']
            relation = form.cleaned_data['relation']

            user = User.objects.create_user(username=email, email=email, password=password)
            hh = Household.objects.create(name=_gen_household_name(email), owner=user)

            Member.objects.create(
                household = hh, display_name = name, nickname = nickname,
                relation_to_admin = {'本人': 'self', '配偶者': 'spouse', '親': 'parent', '子': 'child', 'その他': 'other'}.get(relation, 'other'),
                role = 'admin', user = user
            )
            login(request, user)
            request.session[HK] = hh.id
            return redirect('profiles')
    else:
        form = AdminSignupForm()
    return render(request, 'user/owner_signup.html', {'signup_form': form})

class AdminLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if not user:
                messages.error(request, 'メールアドレスまたはパスワードが正しくありません。'); return redirect('admin_login')
            login(request, user)
            hh = Household.objects.filter(owner=user).first()
            request.session[HK] = hh.id if hh else None
            return redirect('profiles')
    else:
        form = AdminLoginForm()
    return render(request, 'user/admin_login.html', {'form': form})

def join_verify(request):
    if request.method == 'POST': return redirect('welcome')
    form = JoinCodeForm(request.POST)
    if not form.is_valid():
        messages.error(request, '8桁の参加コードを入力してください'); return redirect('welcome')

    code = form.cleaned_data['code8']
    with transaction.atomic():
        jc = (JoinCode.objects.select_for_update().filter(code8=code).first())
        if not jc or not jc.is_valid():
            messages.error(request, '無効な参加コードです'); return redirect('welcome')
        jc.used_at = timezone.now()
        jc.save(update_fields=['used_at'])
        request.session[HK] = jc.household.id
    return redirect('profiles')


def profiles(request, pk:int):
    hh_id = request.session.get(HK)
    if not hh_id: return redirect('welcome')
    m = get_object_or_404(Member, id=pk, household_id=hh_id)
    form = PinForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        pin = form.cleaned_data['pin']
        # 初回設定
        if not m.pin_hash:
            m.pin_hash = make_password(pin)
            m.pin_updated_at = timezone.now()
            m.failed_attempts = 0
            m.locked_until = None
            m.save()
            request.session[MK] = m.id
            request.session[LS] = timezone.now().timestamp()
            return redirect('dashboard')
        # ロック中
        if m.locked_until and m.locked_until > timezone.now():
            messages.error(request, '試行が多すぎます。しばらくしてから再試行してください')
            return redirect('profiles')
        # 照合
        if check_password(pin, m.pin_hash):
            m.failed_attempts = 0
            m.locked_until = None
            m.save(update_fields=['failed_attempts', 'locked_until'])
            request.session[MK] = m.id
            request.session[LS] = timezone.now().timestamp()
            return redirect('dashboard')
        else:
            m.failed_attempts += 1
            if m.failed_attempts >= 5:
                m.locked_until = timezone.now() + timedelta(mitnutes=15)
            m.save(update_fields=['failed_attempts', 'locked_until'])
            messages.error(request, 'PINが違います')
            return redirect('profiles')
    return render(request, 'user/profiles.html', {'member': m, 'form': form})
