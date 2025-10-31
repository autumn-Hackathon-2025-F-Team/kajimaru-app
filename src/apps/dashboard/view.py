from datetime import timedelta
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import Task, Maintenance
from apps.user.models import Users

class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = "home.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        login_user = Users.objects.filter(user=self.request.user).first()

        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        #今日の家事
        tasks_today = Task.objects.filter(daily__date=today, user=login_user).select_related("user")

        #今日の達成率
        total_count = tasks_today.count()
        done_count = tasks_today.filter(is_completed=True).count()
        completion_rate = round(done_count * 100/total_count) if total_count else 0

        #未完了
        unfinished_today = tasks_today.filter(is_completed=False)

        #代役がまだ見つかってない
        need_substitute = tasks_today.filter(is_busy=True, substitute="")

        #昨日できなかった家事
        unfinished_yesterday = Task.objects.filter(daily__date=yesterday, user=login_user, is_completed=False)

        #今日のメンテナンステーブルの作業
        maintenance_today = Maintenance.objects.filter(
            next_date=today, task__user=login_user
        ).select_related("task")

        #フロントに渡す
        context.update({
            "tasks_today": tasks_today,
            "unfinished_today": unfinished_today,
            "need_substitute": need_substitute,
            "unfinished_yesterday": unfinished_yesterday,
            "completion_rate": completion_rate,
            "maintenance_today": maintenance_today,
        })
        return context