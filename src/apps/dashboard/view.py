from datetime import timedelta
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import Task, Maintenance, TaskList
from apps.user.models import Users

class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = "dashboard/home.html"
    login_url = "/login/"

    def get_login_user(self):
        return Users.objects.select_related("household").filter(user=self.request.user).first()

    def get_household(self, login_user: Users):
        return Users.objects.filter(household=login_user.household)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        login_user = self.get_login_user()
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        #今日の家事(個人)
        tasks_today = Task.objects.filter(daily__date=today, user=login_user).select_related("user")

        #未完了
        unfinished_today = tasks_today.filter(is_completed=False)

        #代役がまだ見つかってない
        need_substitute = tasks_today.filter(is_busy=True, substitute="")

        #昨日できなかった家事
        unfinished_yesterday = Task.objects.filter(daily__date=yesterday, user=login_user, is_completed=False)

        #今日のメンテナンステーブルの作業
        maintenance_today = Maintenance.objects.filter(next_date__date=today, task__user=login_user).select_related("task","task__user")

        #家族版
        family = self.get_household(login_user)
        tasks_today_family = Task.objects.filter(daily__date=today, user__in=family).select_related("user")
        unfinished_yesterday_family = Task.objects.filter(daily__date=yesterday, user__in=family, is_completed=False).select_related("user")

        #達成率
        total_count_family = tasks_today_family.count()
        done_count_family = tasks_today_family.filter(is_completed=True).count()
        completion_rate_family = round(done_count_family * 100 / total_count_family) if total_count_family else 0

        maintenance_today_family = Maintenance.objects.filter(next_date__date=today, task__user__in=family).select_related("task","task__user")

        # #家族の家事(1週間分)未完成
        # weekday_today = today.weekday()
        # weekday_tasks_family = [(weekday_today + i) % 7 for i in range(7)]
        # chores_weekday_by_frequency = TaskList.objects.filter(task__user__in=family, frequency__in=weekday_tasks_family).select_related("task", "task__user")

        #フロントに渡す
        context.update({
            "tasks_today": tasks_today,
            "unfinished_today": unfinished_today,
            "need_substitute": need_substitute,
            "unfinished_yesterday": unfinished_yesterday,
            "maintenance_today": maintenance_today,

            #家族
            "tasks_today_family": tasks_today_family,
            "unfinished_yesterday_family": unfinished_yesterday_family,
            "completion_rate_family": completion_rate_family,
            "maintenance_today_family": maintenance_today_family,
            # "chores_weekday_by_frequency": chores_weekday_by_frequency,
        })
        return context
