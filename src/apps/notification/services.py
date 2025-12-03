from collections import defaultdict
from datetime import timedelta
import json
import urllib.request
from django.conf import settings
from django.utils import timezone
from apps.dashboard.models import Task, TaskList, Maintenance
from apps.user.models import Users

def get_user_display_name(user: Users) -> str:
    if hasattr(user, "nickname") and user.nickname:
        return user.nickname
    if hasattr(user, "user"):
        return user.user.username
    return str(user.pk)

def send_mattermost(text: str):
    webhook_url = settings.MATTERMOST_WEBHOOK_URL
    message = f"@all\n{text}"
    payload = {"text": message}
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"Mattermost 送信エラー: {e}")

#前日の家事担当通知
def build_tomorrow_tasks_message() -> str:
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    tasks = Task.objects.filter(daily__date=tomorrow).select_related("user", "task_list").order_by("user__id")

    if not tasks.exists():
        return None

    by_user = defaultdict(list)
    for t in tasks:
        if t.user:
            by_user[t.user].append(t.task_list.task_name)

    lines = [f"【明日の家事担当のお知らせ】✨\n明日 ({tomorrow}) の家事一覧です。"]
    for user, task_names in by_user.items():
        name = get_user_display_name(user)
        joined = " / ".join(task_names)
        lines.append(f"- {name}: {joined}")
    return "\n".join(lines)

def notify_tomorrow_tasks():
    msg = build_tomorrow_tasks_message()
    if msg:
        send_mattermost(msg)

#当日の家事担当通知
def build_today_tasks_message() -> str:
    today = timezone.localdate()
    tasks = Task.objects.filter(daily__date=today).select_related("user", "task_list").order_by("user__id")

    if not tasks.exists():
        return None

    by_user = defaultdict(list)
    for t in tasks:
        if t.user:
            by_user[t.user].append(t.task_list.task_name)

    lines = [f"【本日の家事担当のお知らせ】✨\n本日 ({today}) の家事一覧です。"]
    for user, task_names in by_user.items():
        name = get_user_display_name(user)
        joined = " / ".join(task_names)
        lines.append(f"- {name}: {joined}")
    return "\n".join(lines)

def notify_today_tasks():
    msg = build_today_tasks_message()
    if msg:
        send_mattermost(msg)

#遅延通知
def build_unfinished_yesterday_message() -> str:
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    unfinished = Task.objects.filter(daily__date=yesterday, is_completed=False).select_related("user", "task_list").order_by("user__id")
    if not unfinished.exists():
        return None

    by_user = defaultdict(list)
    for t in unfinished:
        if t.user:
            by_user[t.user].append(t.task_list.task_name)
        else:
            by_user[None].append(t.task_list.task_name)

    lines = [f"【昨日の未完了家事のお知らせ】⚠️\n昨日 ({yesterday}) の未完了家事一覧です。"]
    for user, task_names in by_user.items():
        name = get_user_display_name(user) if user else "担当なし"
        joined = " / ".join(task_names)
        lines.append(f"- {name}: {joined}")
    return "\n".join(lines)

def notify_unfinished_yesterday():
    msg = build_unfinished_yesterday_message()
    if msg:
        send_mattermost(msg)

def build_monthly_assignment_message() -> str:
    today = timezone.localdate()
    year_month = today.strftime("%Y-%m")

    maints = Maintenance.objects.prefetch_related("homemakers").order_by("id")

    if not maints.exists():
        return f"【{year_month} のMaintenance担当一覧】\n今月のMaintenanceはありません🎉"

    lines = [f"【{year_month} の担当一覧】"]
    for tl in maints:
        homemakers = tl.homemakers.all()
        if homemakers:
            names = ", ".join(get_user_display_name(user) for user in homemakers)
        else:
            names = "担当者未割当"
        lines.append(f"- {tl.task_name}: {names}")

    return "\n".join(lines)

def notify_monthly_assignment():
    msg = build_monthly_assignment_message()
    send_mattermost(msg)