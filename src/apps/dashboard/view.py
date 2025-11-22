from datetime import timedelta
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.shortcuts import redirect
from .models import Task, Maintenance, TaskList
from apps.user.models import Users
from apps.rotation.services import create_week_tasks, create_maintenance_tasks, reset_future_tasks

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
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        #今日の家事(個人)
        tasks_today = Task.objects.filter(daily__date=today, user=login_user).select_related("user","task_list","maintenance")

        #昨日できなかった家事
        unfinished_yesterday = Task.objects.filter(daily__date=yesterday, user=login_user, is_completed=False).select_related("user","task_list","maintenance")

        #今日のメンテナンステーブルの作業
        maintenance_today = Maintenance.objects.filter(next_date__date=today, homemakers=login_user).select_related("homemakers")

        #家族版
        family = self.get_household(login_user)
        tasks_today_family = Task.objects.filter(daily__date=today, user__in=family).select_related("user","task_list","maintenance")
        unfinished_yesterday_family = Task.objects.filter(daily__date=yesterday, user__in=family, is_completed=False).select_related("user")

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
        })
        return context

    def post(self, request, *args, **kwargs):
        today = timezone.localdate()
        reset_future_tasks()
        create_week_tasks()
        create_maintenance_tasks(run_date=today)
        return redirect("dashboard:dashboard")

