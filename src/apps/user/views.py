from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AdminSignupForm, JoinCodeForm, PinSetForm, PinVerifyForm, AdminLoginForm, MemberForm, AdminPinForm, AvatarUpdateForm
from django.utils.crypto import get_random_string
from .models import Household, Users, JoinCode
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from django.http import HttpResponse
from .models import Users as Member

HK = "household_id"
MK = 'active_member_id'
LS = 'profile_last_seen'
PIN_MAX_TRIES = 5
PIN_LOCK_MINUTES =15


def _gen_household_name(email: str) -> str:
    return f"household-{email.split('@')[0]}-{get_random_string(6)}"

def index(request):
    return render(request, 'user/index.html')

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
        messages.error(request, '8桁の招待コードを入力してください'); 
        return redirect('welcome')

    code = form.cleaned_data['code8']
    with transaction.atomic():
        jc = (JoinCode.objects.select_for_update().filter(code8=code).first())
        if not jc or not jc.is_valid():
            messages.error(request, '無効な招待コードです'); return redirect('welcome')
        if jc.used_at is None:
            jc.used_at = timezone.now()
            jc.max_uses = timezone.now()
            jc.save(update_fields=['used_at'])
        request.session[HK] = jc.household.id
        
    return redirect('profiles_list')


def profiles(request, pk:int):
    hh_id = request.session.get(HK)
    if not hh_id:
        return redirect('welcome')
    m = get_object_or_404(Users, id=pk, household_id=hh_id)
    now = timezone.now()

    if m.locked_until and m.locked_until <= now:
        m.failed_attempts = 0
        m.locked_until = None
        m.save(update_fields=['failed_attempts', 'locked_until'])
    
    if request.method != 'POST':
        if m.locked_until and m.locked_until > now:
            remaining = int((m.locked_until - now).total_seconds())
            return render(request, 'user/login_error.html', {
                'member': m,
                'remaining_seconds': remaining,
                'lock_minutes': PIN_LOCK_MINUTES,
            })
        form = PinSetForm()
        return render(request, 'user/profiles.html', {'member': m, 'form': form})
    
    form = PinSetForm(request.POST)
    if not form.is_valid():
        return render(request, 'user/profiles.html', {'member': m, 'form': form})
    
    if m.locked_until and m.locked_until > now:
        remaining = int((m.locked_until - now).total_seconds())
        return render(request, 'user/login_error.html', {
            'member': m,
            'remaining_seconds': remaining,
            'lock_minutes': PIN_LOCK_MINUTES,
        })
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
        return render(request, 'user/invite_result.html')
    
    def _gen_code():
        return get_random_string(length=8, allowed_chars='0123456789')
    
    with transaction.atomic():
        now = timezone.now()
        (
            JoinCode.objects
            .select_for_update()
            .filter(
                household=hh,
                revoked=False,
                used_at__isnull=True,
                expires_at__gt=now,
            )
            .update(expires_at=now)
        )
        for _ in range(10):
            code = _gen_code()
            exists = JoinCode.objects.select_for_update().filter(code8=code).exists()
            if not exists:
                jc = JoinCode.objects.create(
                    code8 =code,
                    household = hh,
                    expires_at = timezone.now() + timedelta(minutes=5),
                    revoked=False,
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

# # 岡が追記した分↓
# def personal_page(request, pk:int):
#     """個人のプロフィール"""
#     hh_id = request.session.get(HK)
#     if not hh_id:
#         return redirect('welcome')
#     m = get_object_or_404(Users, id=pk, household_id=hh_id)
#     return render(request, 'user/personal_page.html', {'m': m})
# # ↑ここまで

def profile_enter(request, pk:int):
    """プロフィール別PIN（初回は設定）"""
    hh_id = request.session.get(HK)
    if not hh_id:
        return redirect('welcome')
    
    m = get_object_or_404(Users, id=pk, household_id=hh_id)
    
    if not m.pin_hash:
        form = PinSetForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            pin = form.cleaned_data['pin1']
            m.pin_hash = make_password(pin)
            m.pin_updated_at = timezone.now()
            m.failed_attempts = 0
            m.locked_until = None
            m.save(update_fields=['pin_hash', 'pin_updated_at', 'failed_attempts', 'locked_until'])
            request.session[MK] = m.id
            request.session[LS] = timezone.now().timestamp()
            request.session["active_user_id"] = m.id
            return redirect('dashboard:dashboard')
        return render(request, 'user/login.html', {'member': m, 'form': form})
        
    if m.locked_until and m.locked_until > timezone.now():
        messages.error(request, '試行が多すぎます。しばらくしてから再試行してください')
        return redirect('profiles_list')
    
    form = PinVerifyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        pin = form.cleaned_data['pin']
        if check_password(pin, m.pin_hash):
            m.failed_attempts = 0
            m.locked_until = None
            m.save(update_fields=['failed_attempts', 'locked_until'])
            request.session[MK] = m.id
            request.session[LS] = timezone.now().timestamp()
            request.session["active_user_id"] = m.id
            return redirect("dashboard:dashboard")
        else:
            m.failed_attempts += 1
            if m.failed_attempts >= 5:
                m.locked_until = timezone.now() + timedelta(minutes=15)
            m.save(update_fields=['failed_attempts', 'locked_until'])
            messages.error(request, 'PINが違います')
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
            name = form.cleaned_data["display_name"].strip()

            if Users.objects.filter(household=hh, display_name__iexact=name).exists():
                form.add_error("display_name", "この名前は世帯内で使用済みです")
            else:
                member = form.save(commit=False)
                member.household = hh
                member.save()
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
def member_edit(request, pk: int):
    hh = _require_admin_household(request)
    if not hh:
        messages.error(request, '管理者の世帯が見つかりません。')
        return redirect('admin_login')
    
    member = get_object_or_404(Users, id=pk, household=hh)

    if request.method == 'POST':
        # 既存データに対する更新なので instance=member を渡す
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            name = form.cleaned_data['display_name'].strip()

            # 自分以外に同名がいないかチェック
            dup_exists = (
                Users.objects
                .filter(household=hh, display_name__iexact=name)
                .exclude(id=member.id)   # ← ここを m ではなく member に統一
                .exists()
            )
            if dup_exists:
                form.add_error('display_name', 'この名前は世帯内で使用済みです')
            else:
                form.save()  # avatar_key 含めて保存
                messages.success(request, f'プロフィール「{name}」を更新しました')
                return redirect('admin_user')

        # バリデーションNG時
        return render(
            request,
            'user/owner_family_manage.html',
            {'form': form, 'mode': 'edit', 'member': member}
        )

    # GET時：初期表示
    form = MemberForm(instance=member)
    return render(
        request,
        'user/owner_family_manage.html',
        {'form': form, 'mode': 'edit', 'member': member}
    )

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
        return redirect('admin_user')
    return render(request, 'user/member_delete_confirm.html', {'member': m})

@login_required
def admin_gate(request):
    """
    管理者ページ専用のPINゲート。
    - GET: PIN入力フォーム表示
    - POST: 管理者メンバーのPIN照合 → OKなら /owner/user/ へ
    """
    hh = _require_admin_household(request)
    if not hh:
        messages.error(request, '管理者の世帯が見つかりません。ログインし直してください。')
        return redirect('admin_login')

    # 世帯内の管理者メンバー（Usersモデル）を取得
    admin_member = Users.objects.filter(household=hh, role='admin').first()
    if not admin_member:
        messages.error(request, '管理者プロフィールが未作成です。先に作成してください。')
        return redirect('family_member_add')

    if request.method == 'POST':
        form = AdminPinForm(request.POST)
        if form.is_valid():
            pin = form.cleaned_data['pin']

            # ロック中チェック
            if admin_member.locked_until and admin_member.locked_until > timezone.now():
                remain = int((admin_member.locked_until - timezone.now()).total_seconds() // 60) + 1
                messages.error(request, f'試行が多すぎます。{remain}分後に再試行してください。')
                return redirect('admin_gate')

            # 初回PIN未設定なら設定として扱う（必要なければ削除）
            if not admin_member.pin_hash:
                admin_member.pin_hash = make_password(pin)
                admin_member.pin_updated_at = timezone.now()
                admin_member.failed_attempts = 0
                admin_member.locked_until = None
                admin_member.save(update_fields=['pin_hash', 'pin_updated_at', 'failed_attempts', 'locked_until'])
                # セッションに管理者メンバーをセットして管理者ページへ
                request.session[MK] = admin_member.id
                request.session[LS] = timezone.now().timestamp()
                return redirect('admin_user')

            # 照合
            if check_password(pin, admin_member.pin_hash):
                admin_member.failed_attempts = 0
                admin_member.locked_until = None
                admin_member.save(update_fields=['failed_attempts', 'locked_until'])
                request.session[MK] = admin_member.id
                request.session[LS] = timezone.now().timestamp()
                return redirect('admin_user')
            else:
                admin_member.failed_attempts = (admin_member.failed_attempts or 0) + 1
                if admin_member.failed_attempts >= 5:
                    # ※ 以前のコードで mitnutes typo あり。minutes に修正！
                    admin_member.locked_until = timezone.now() + timedelta(minutes=15)
                admin_member.save(update_fields=['failed_attempts', 'locked_until'])
                messages.error(request, '管理者PINが違います')
                return redirect('admin_gate')
        # バリデーションNG
        return render(request, 'user/admin_gate.html', {'form': form})

    # GET
    form = AdminPinForm()
    return render(request, 'user/admin_gate.html', {'form': form})

@login_required
def admin_user(request):
    hh = _require_admin_household(request)
    if not hh:
        messages.error(request, '管理者権限が必要です。')
        return redirect('admin_login')
    members = Users.objects.filter(household=hh).order_by('id')
    return render(request, 'user/admin_user.html', {'members': members})

@login_required
def pin_reset(request, pk:int):
    hh = _require_admin_household(request)
    if not hh:
        messages.error(request, '管理者の世帯が見つかりません。')
        return redirect('admin_login')
    
    member = get_object_or_404(Member, id=pk, household=hh)
    if request.method == 'POST':
        new_pin = (request.POST.get('new_pin') or '').strip()
        confirm_pin = (request.POST.get('confirm_pin') or '').strip()
        unlock = request.POST.get('unlock') == '1'

        if not (new_pin.isdigit() and len(new_pin) == 4):
            messages.error(request, 'PINは数字4桁で入力してください。')
        elif new_pin != confirm_pin:
            messages.error(request, '確認用PINが一致しません。')
        else:
            member.pin_hash = make_password(new_pin)
            member.pin_updated_at = timezone.now()
            if unlock:
                member.failed_attempts = 0
                member.locked_until = None
            member.save(update_fields=['pin_hash', 'pin_updated_at', 'failed_attempts', 'locked_until'])
            messages.success(request, f'{member.display_name}のPINを更新しました。')
            return redirect('admin_user')
    return render(request, 'user/pin_reset.html', {'member': member})

@login_required
def avatar_edit(request, pk: int):
    hh = _require_admin_household(request)
    member = get_object_or_404(Users, id=pk, household=hh)

    # ハードコードした許可キー
    allowed = {"boy", "girl", "man", "woman"}

    if request.method == "POST":
        key = request.POST.get("avatar_key", "")
        if key in allowed:
            member.avatar_key = key
            member.save(update_fields=["avatar_key"])
            messages.success(request, "アイコンを更新しました。")
            return redirect("profiles_list")
        messages.error(request, "アイコンを選択してください。")

    return render(request, "user/avatar_edit.html", {"member": member})        
