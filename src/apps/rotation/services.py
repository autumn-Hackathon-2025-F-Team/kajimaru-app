from datetime import timedelta, datetime
import random
from django.utils import timezone
from apps.dashboard.models import TaskList, Task, WEEKDAY_FLAGS, Maintenance
from apps.user.models import Users

def calc_user_score_for_tasklist(task_list: TaskList, user: Users) -> int:
    now = timezone.now()
    since = now - timedelta(days=90)
    #家事の履歴取得
    qs = Task.objects.filter(
        task_list=task_list,
        user=user,
        daily__gte=since,
    )
    #完了した家事の履歴取得
    completed_qs = qs.filter(is_completed=True)
    completed_count = completed_qs.count()
    #完了した家事の重みの合計
    weight_sum = completed_count * task_list.weight
    #未完了の家事がある場合はペナルティ
    has_unfinished = qs.filter(is_completed=False).exists()
    penalty = -2 if has_unfinished else 0
    #件数＋重み＋ペナルティ
    score = completed_count + weight_sum + penalty
    return score

#ルーレットで使う重み
def scores_to_weights(scores: dict[Users, int]) -> dict[Users, float]:
    weights: dict[Users, float] = {}
    for user, score in scores.items():      #items=dictのkeyとvalueを取得
        effective = max(score, 1)       #1未満は1に補正(割り算で0になるのを防ぐ)
        weights[user] = 1.0 / float(effective)      #ルーレットの重みを計算
    return weights

#ルーレット本体
def roulette_choice(weights: dict[Users, float]) -> Users | None:
    total = sum(weights.values())       #全員の重みの合計
    r = random.uniform (0,total)        #0から合計値までの乱数を取得
    upto = 0.0                 #ルーレットの目盛り
    for user, w in weights.items():
        upto += w       #ルーレットの位置を決める(重み分だけ進む)
        if upto >= r:    #乱数の位置とルーレットの位置を比較
            return user
    return list(weights.keys())[-1]

#担当者決定
def choose_homemaker_for_tasklist(task_list: TaskList) -> Users | None:
    candidates = list(task_list.homemakers.exclude(status="busy"))       #DB負担軽減のためのリスト化
    if not candidates:      #候補者がいなければNoneを返す
        return None
    scores: dict[Users, int] = {}
    for user in candidates:      #候補者を一人ずつ取り出してスコアを計算
        scores[user] = calc_user_score_for_tasklist(task_list, user)
    weights = scores_to_weights(scores)
    winner = roulette_choice(weights)       #ルーレットで当選者を決定
    return winner

#Pythonの曜日"0=月曜〜6=日曜"をビットフラグに変換する辞書
BIT_BY_WEEKDAY: dict[int, int] = {
    idx: bit for idx, (bit, label) in enumerate(WEEKDAY_FLAGS)
}

#週ローテ家事のタスクを１週間分まとめて作成する
def create_week_tasks(run_date=None):
    today = timezone.localdate()
    if run_date is None:
        run_date = today - timedelta(days=today.weekday())        #今週の月曜日を取得
    end_date = run_date + timedelta(days=7)       #翌週の月曜日を取得
    task_lists = TaskList.objects.prefetch_related("homemakers")        #DB負担軽減のためのリスト化
    for tl in task_lists:
        for i in range(7):      #1週間分ループ
            day = run_date + timedelta(days=i)
            if day < today:      #過去日はスキップ
                continue
            py_weekday = day.weekday()
            bit = BIT_BY_WEEKDAY[py_weekday]

            if not (tl.frequency & bit):        #その曜日に家事が設定されていなければスキップ
                continue
            if Task.objects.filter(task_list=tl, daily=day).exists():      #すでにタスクが存在する場合はスキップ
                continue
            homemaker = choose_homemaker_for_tasklist(tl)       #担当者を決定
            if not homemaker:
                continue      #担当者が決まらなければスキップ
            Task.objects.create(        #DBに登録
                task_list=tl,       #家事
                user=homemaker,      #担当者
                daily=timezone.make_aware(        #日時をタイムゾーン対応に変換
                    datetime.combine(day, datetime.min.time())
                ),
                role=homemaker.display_name,
            )

def reset_future_tasks():
    today = timezone.localdate()
    Task.objects.filter(daily__gte=today,).delete()

#Maintenance用
def calc_user_score_for_maintenance(maintenance: Maintenance, user: Users) -> int:
    now = timezone.now()
    since = now - timedelta(days=90)
    qs = Task.objects.filter(
        maintenance=maintenance,
        user=user,
        daily__gte=since,
    )
    completed_qs = qs.filter(is_completed=True)
    completed_count = completed_qs.count()

    weight_sum = completed_count
    has_unfinished = qs.filter(is_completed=False).exists()
    penalty = -2 if has_unfinished else 0

    score = completed_count + weight_sum + penalty
    return score

#Maintenance担当者決定
def choose_homemaker_for_maintenance(maintenance: Maintenance) -> Users | None:
    candidates = list(maintenance.homemakers.exclude(status="busy"))
    if not candidates:
        return None
    scores: dict[Users, int] = {}
    for user in candidates:
        scores[user] = calc_user_score_for_maintenance(maintenance, user)
    weights = scores_to_weights(scores)
    winner = roulette_choice(weights)
    return winner

#月ローテを毎月1日まとめて作成する
def create_maintenance_tasks(run_date=None):
    if run_date is None:
        run_date = timezone.localdate()
    if run_date.day != 1:
        return
    maintenance_tasks = Maintenance.objects.prefetch_related("homemakers").filter(
        next_date__year=run_date.year,
        next_date__month=run_date.month,
    )

    for m in maintenance_tasks:
        homemaker = choose_homemaker_for_maintenance(m)
        if not homemaker:
            continue
        Task.objects.create(
            maintenance=m,
            user=homemaker,
            daily=m.next_date,
            role=homemaker.display_name,
        )