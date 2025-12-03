from datetime import timedelta
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Task, Maintenance, TaskList
from apps.user.models import Users
from apps.rotation.services import create_week_tasks, create_maintenance_tasks, reset_future_tasks

def get_login_user(request):
    active_id = request.session.get("active_user_id")
    if active_id:
        return Users.objects.select_related("household").filter(id=active_id).first()
    return Users.objects.select_related("household").filter(user=request.user).first()
class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = "dashboard/home.html"
    login_url = "/login/"

    def get_login_user(self):
        active_id = self.request.session.get("active_user_id")
        if active_id:
            return Users.objects.select_related("household").filter(id=active_id).first()
        return Users.objects.select_related("household").filter(user=self.request.user).first()

    def get_household(self, login_user: Users):
        if not login_user or not login_user.household:
            return Users.objects.none()
        return Users.objects.filter(household=login_user.household)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        login_user = self.get_login_user()
        family = self.get_household(login_user)
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        #代役募集中のタスク
        substitute_requests = Task.objects.filter(user__in=family,is_busy=True,is_completed=False,).exclude(user=login_user).select_related("user","task_list").order_by("daily")
        context["substitute_requests"] = substitute_requests

        #今日の家事(個人)
        tasks_today = Task.objects.filter(daily=today, user=login_user).select_related("user","task_list","maintenance")

        #昨日できなかった家事
        unfinished_yesterday = Task.objects.filter(daily=yesterday, user=login_user, is_completed=False).select_related("user","task_list","maintenance")

        #今日のメンテナンステーブルの作業
        maintenance_today = Maintenance.objects.filter(next_date__date=today, homemakers=login_user).select_related("homemakers")

        #家族版
        family = self.get_household(login_user)
        tasks_today_family = Task.objects.filter(daily=today, user__in=family).select_related("user","task_list","maintenance")
        unfinished_yesterday_family = Task.objects.filter(daily=yesterday, user__in=family, is_completed=False).select_related("user")

        #達成率
        total_count_family = tasks_today_family.count()
        done_count_family = tasks_today_family.filter(is_completed=True).count()
        completion_rate_family = round(done_count_family * 100 / total_count_family) if total_count_family else 0

        maintenance_today_family = Maintenance.objects.filter(next_date__date=today, homemakers__in=family).distinct().prefetch_related("homemakers")

        #家族の家事(1週間分)
        weekday_today = today.weekday()
        weekday_labels = ["月曜日","火曜日","水曜日","木曜日","金曜日","土曜日","日曜日"]

        tasklists_family = TaskList.objects.filter(homemakers__in=family).prefetch_related("homemakers").distinct()

        chores_weekday_by_frequency = []
        for i in range(7):
            weekday = (weekday_today + i) % 7
            weekday_bit = 1 << weekday

            tasks_for_day = [
                tl for tl in tasklists_family if tl.frequency & weekday_bit
            ]

            chores_weekday_by_frequency.append({
                "weekday_index": weekday,
                "weekday_label": weekday_labels[weekday],
                "date": today + timedelta(days=i),
                "tasklists": tasks_for_day,
            })

        can_run_week_tasks = self.request.user.is_staff

        # 週ローテ用追加
        # 今週（月〜日）の開始・終了
        week_start = today - timedelta(days=weekday_today)   # 今週の月曜
        week_end = week_start + timedelta(days=6)            # 今週の日曜

        week_dates = [week_start + timedelta(days=i) for i in range(7)]

        # 今週1週間分の Task（家族全員分）
        week_tasks_qs = (
            Task.objects
            .filter(
                daily__gte=week_start,
                daily__lte=week_end,
                user__in=family,
            )
            .select_related("task_list", "user")
        )

        # (task_list_id, date) → 担当者名 のマップ
        task_map = {}
        for t in week_tasks_qs:
            task_date = t.daily
            key = (t.task_list_id, task_date)
            task_map[key] = t.user.nickname if t.user else ""

        # JS に渡す「表1行分」のデータ
        # 1行 = 1つの家事（task_name）＋ 7日分の担当者名
        week_rotation_data = []
        for tl in tasklists_family:
            row = {
                "task_name": tl.task_name,
                "names": [],
            }
            for d in week_dates:
                name = task_map.get((tl.id, d), "")
                row["names"].append(name)
            week_rotation_data.append(row)
        # 追加ここまで
        
        #代役タスク
        pending_sub_tasks = Task.objects.filter(
            daily=today,
            user__in=family,
            is_busy=True,
            is_completed=False,
        ).select_related("user","task_list","maintenance")

        #フロントに渡す
        context.update({
            "tasks_today": tasks_today,
            "unfinished_yesterday": unfinished_yesterday,
            "maintenance_today": maintenance_today,

            #家族
            "tasks_today_family": tasks_today_family,
            "unfinished_yesterday_family": unfinished_yesterday_family,
            "completion_rate_family": completion_rate_family,
            "maintenance_today_family": maintenance_today_family,
            "chores_weekday_by_frequency": chores_weekday_by_frequency,
            "can_run_week_tasks": can_run_week_tasks,

            # 週ローテ
            "week_rotation_data": week_rotation_data,
             
            #代役
            "login_user": login_user,
            "pending_sub_tasks": pending_sub_tasks,
        })
        return context

    def post(self, request, *args, **kwargs):
        today = timezone.localdate()
        reset_future_tasks()
        create_week_tasks(run_date=today)
        create_maintenance_tasks(run_date=today)
        return redirect("dashboard:dashboard")

class ToggleTaskDoneView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        task.is_completed = not task.is_completed
        task.save(update_fields=["is_completed"])
        today = timezone.localdate()
        active_id = request.session.get("active_user_id")
        if active_id:
            login_user = Users.objects.select_related("household").filter(id=active_id).first()
        else:
            login_user = Users.objects.select_related("household").filter(user=request.user).first()

        if not login_user or not login_user.household:
            family = Users.objects.none()
        else:
            family = Users.objects.filter(household=login_user.household)

        tasks_today_family = Task.objects.filter(daily=today, user__in=family)
        total_count_family = tasks_today_family.count()
        done_count_family = tasks_today_family.filter(is_completed=True).count()
        completion_rate_family = round(done_count_family * 100 / total_count_family) if total_count_family else 0

        return JsonResponse({
            "success": True,
            "is_completed": task.is_completed,
            "completion_rate_family": completion_rate_family,
            "done_count_family": done_count_family,
            "total_count_family": total_count_family,
        })
@login_required
@require_POST
def request_substitute(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    login_user = get_login_user(request)
    #完了済みなら依頼不可
    if task.is_completed:
        return HttpResponseForbidden("完了済みのタスクには代役依頼できません")
    #すでに代役依頼中なら不可
    if task.is_busy:
        return redirect("dashboard:dashboard")

    task.is_busy = True
    task.save(update_fields=["is_busy"])
    return redirect("dashboard:dashboard")

@login_required
@require_POST
def accept_substitute(request, task_id):
    approver = get_login_user(request)
    if not approver or not approver.household_id:
        return HttpResponseForbidden("世帯情報がありません")
    with transaction.atomic():
        task = (
            Task.objects
            .select_for_update()
            .select_related("user")
            .get(pk=task_id)
        )
        if not task.is_busy:
            return redirect("dashboard:dashboard")

        if task.user is None:
            return HttpResponseForbidden("担当者情報がありません")
        if task.user.household_id != approver.household_id:
            return HttpResponseForbidden("権限がありません")
        original_user = task.user
        task.substitute = original_user.display_name
        task.user = approver
        task.is_busy = False
        task.save(update_fields=["user", "substitute", "is_busy"])
    return redirect("dashboard:dashboard")

@login_required
@require_POST
def toggle_busy(request):
    login_user = get_login_user(request)
    if not login_user:
        return HttpResponseForbidden("ログインユーザーが取得できません")

    if login_user.status == "busy":
        login_user.status = "active"
    else:
        login_user.status = "busy"
    login_user.save(update_fields=["status"])
    return redirect("dashboard:dashboard")