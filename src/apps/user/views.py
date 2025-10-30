from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AdminSignupForm, JoinCodeForm, PinForm, AdminLoginForm, MemberForm
from django.utils.crypto import get_random_string
from .models import Household, Users, JoinCode
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
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']
            nickname = form.cleaned_data.get('nickname', '')
            relation = form.cleaned_data['relation']

            user = User.objects.create_user(username=email, email=email, password=password)
            hh = Household.objects.create(name=_gen_household_name(email), owner=user)

            Users.objects.create(
                household = hh, display_name = name, nickname = nickname,
                relation_to_admin = {'本人': 'self', '配偶者': 'spouse', '親': 'parent', '子': 'child', 'その他': 'other'}.get(relation, 'other'),
                role = 'admin', user = user
            )
            login(request, user)
            request.session[HK] = hh.id
            return redirect('member_create')
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
            return redirect('profiles_list')
    else:
        form = AdminLoginForm()
    return render(request, 'user/owner_login.html', {'form': form})

def join_verify(request):
    if request.method != 'POST': 
        return redirect('welcome')
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
    return redirect('profiles_list')


def profiles(request, pk:int):
    hh_id = request.session.get(HK)
    if not hh_id: return redirect('welcome')
    m = get_object_or_404(Users, id=pk, household_id=hh_id)
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
            return redirect('profiles_list')
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
                m.locked_until = timezone.now() + timedelta(minutes=15)
            m.save(update_fields=['failed_attempts', 'locked_until'])
            messages.error(request, 'PINが違います')
            return redirect('profiles_list')
    return render(request, 'user/profiles.html', {'member': m, 'form': form})

def _require_admin_household(request):
    if not request.user.is_authenticated:
        return None
    hh_id = request.session.get(HK)
    if hh_id:
        return Household.objects.filter(id=hh_id, owner=request.user).first()
    return Household.objects.filter(owner=request.user).first()

@login_required
def invite_create(request):
    """8桁・5分・1回使いきりの招待コード発行"""
    hh = _require_admin_household(request)
    if not hh:
        messages.error(request, '管理者の世帯が見つかりません。ログインし直してください。')
        return redirect('admin_login')
    
    if request.method == 'POST':
        return render(request, 'user/invite_issue.html')
    
    def _gen_code():
        return get_random_string(length=8, allowed_chars='0123456789')
    
    with transaction.atomic():
        for _ in range(10):
            code = _gen_code()
            exists = JoinCode.objects.select_for_update().filter(code8=code).exists()
            if not exists:
                jc = JoinCode.objects.create(
                    code8 =code,
                    household = hh,
                    expires_at = timezone.now() + timedelta(minutes=5),
                    created_by = request.user,
                )
                break
        else:
            messages.error(request, '招待コードの生成に失敗しました。もう一度お試しください。')
            return redirect('profiles_list')
    return render(request, 'user/invite_result.html', {'code': jc.code8, 'expires_at': jc.expires_at})

def profiles_list(request):
    """世帯のプロフィール一覧"""
    hh_id = request.session.get(HK)
    if not hh_id:
        return redirect('welcome')
    members = Users.objects.filter(household_id=hh_id).order_by('id')
    return render(request, 'user/family_select.html', {'members': members})

def profile_enter(request, pk:int):
    """プロフィール別PIN（初回は設定）"""
    hh_id = request.session.get(HK)
    if not hh_id:
        return redirect('welcome')
    m = get_object_or_404(Users, id=pk, household_id=hh_id)
    form = PinForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        pin = form.cleaned_data['pin']
        if not m.pin_hash:
            m.pin_hash = make_password(pin)
            m.pin_updated_at = timezone.now()
            m.failed_attempts = 0
            m.locked_until = None
            m.save()
            request.session[MK] = m.id
            request.session[LS] = timezone.now().timestamp()
            return redirect('dashboard')
        
        if m.locked_until and m.locked_until > timezone.now():
            messages.error(request, '試行が多すぎます。しばらくしてから再試行してください')
            return redirect('profiles_list')
        
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
                m.locked_until = timezone.now() + timedelta(minutes=15)
            m.save(update_fields=['failed_attempts', 'locked_until'])
            messages.error(request, 'PINが違います')
            return redirect('profile_list')
    return render(request, 'user/profile_enter.html', {'member': m, 'form': form})

# ---- 管理者のプロフィールCRUD ----

@login_required
def member_create(request):
    hh = _require_admin_household(request)
    if not hh:
        messages.error(request, "管理者の世帯が見つかりません。ログインし直してください。")
        return redirect("admin_login")

    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["display_name"]

            # ★ ここで必ず FamilyMember を使う！！
            if Users.objects.filter(household=hh, display_name=name).exists():
                form.add_error("display_name", "この名前は世帯内で使用済みです")
            else:
                Users.objects.create(
                    household=hh,
                    display_name=name,
                    nickname=form.cleaned_data.get("nickname", ""),
                    relation_to_admin=form.cleaned_data["relation"],
                    role=form.cleaned_data["role"],
                    avatar_url=form.cleaned_data.get("avatar_url", ""),
                )
                messages.success(request, f"プロフィール「{name}」を作成しました")
                return redirect("invite_create")

        # バリデーションNG時
        return render(
            request,
            "user/owner_family_manage.html",
            {"form": form, "mode": "create"},
        )

    # GET のとき
    form = MemberForm()
    return render(request, "user/owner_family_manage.html", {"form": form, "mode": "create"})    
@login_required
def member_edit(request, pk:int):
    hh = _require_admin_household(request)
    if not hh:
        messages.error(request, '管理者の世帯が見つかりません。')
        return redirect('admin_login')
    
    m = get_object_or_404(Users, id=pk, household=hh)
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['display_name']
            if Users.objects.filter(household=hh, display_name=name).exlude(id=m.id).exists():
                form.add_error('display_name', 'この名前は世帯内で使用済みです')
            else:
                m.display_name = name
                m.nickname = form.cleaned_data.get('nickname', '')
                m.relation_to_admin = form.cleaned_data['relation']
                m.role = form.cleaned_data['role']
                m.avatar_url = form.cleaned_data.get('avatar_url', '')
                m.save()
                messages.success(request, f'プロフィール「{name}」を更新しました')
                return redirect('profiles_list')
    else:
        form = MemberForm(initial={
            'display_name': m.display_name,
            'nickname': m.nickname,
            'relation': m.relation_to_admin,
            'role': m.role,
            'avatar_url': m.avatar_url,
        })
    return render(request, 'user/owner_family_manage.html', {'form': form, 'mode': 'edit', 'member': m})

@login_required
def member_delete(request, pk:int):
    hh = _require_admin_household(request)
    if not hh:
        messages.error(request, '管理者の世帯が見つかりません。')
        return redirect('admin_login')
    
    m = get_object_or_404(Users, id=pk, household=hh)
    if request.method == 'POST':
        display = m.display_name
        m.delete()
        messages.success(request, f'プロフィール「{display}」を削除しました')
        return redirect('profiles_list')
    return render(request, 'user/member_delete_confirm.html', {'member': m})
