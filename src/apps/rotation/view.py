from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from apps.dashboard.models import TaskList, Maintenance
from .forms import TaskListForm, MaintenanceForm

@login_required
#家事リスト取得、新規作成フォーム、編集フォームの表示
def task_list_view(request):
    task_lists = TaskList.objects.prefetch_related('homemakers').order_by('id')
    create_form = TaskListForm()
    edit_form = TaskListForm()

    context = {
        'task_lists': task_lists,
        'create_form': create_form,
        'edit_form': edit_form,
    }
    return render(request, 'rotation/task_list.html', context)

@login_required
@require_POST
#家事リスト新規(追加)処理
def task_list_create(request):
    form = TaskListForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.save()
        form.save_m2m()
        return redirect('rotation:task_list')

    task_lists = TaskList.objects.prefetch_related('homemakers').order_by('id')
    return render(request, 'rotation/task_list.html',
                {'task_lists': task_lists, 'create_form': form, 'edit_form': TaskListForm()})

@login_required
@require_POST
#家事リスト編集処理
def task_list_edit(request):
    pk = request.POST.get("task_id")
    task_list = get_object_or_404(TaskList, pk=pk)
    form = TaskListForm(request.POST, instance=task_list)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.save()
        form.save_m2m()
        return redirect('rotation:task_list')

    task_lists = TaskList.objects.prefetch_related('homemakers').order_by('id')
    return render(
        request,
        'rotation/task_list.html',
        {'task_lists': task_lists, 'create_form': TaskListForm(), 'edit_form': form}
    )

@login_required
@require_POST
#家事リスト削除処理
def task_list_delete(request):
    pk = request.POST.get("task_id")
    task_list = get_object_or_404(TaskList, pk=pk)
    task_list.delete()
    return redirect('rotation:task_list')

#maintenance処理の実装
@login_required
def maintenance_list_view(request):
    maintenance_tasks = Maintenance.objects.prefetch_related('homemakers').order_by('id')
    create_form = MaintenanceForm()
    edit_form = MaintenanceForm()

    context = {
        'maintenance_tasks': maintenance_tasks,
        'create_form': create_form,
        'edit_form': edit_form,
    }
    return render(request, 'rotation/maintenance_list.html', context)

@login_required
@require_POST
def maintenance_create(request):
    form = MaintenanceForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.save()
        form.save_m2m()
        return redirect('rotation:maintenance_list')

    maintenance_task = Maintenance.objects.prefetch_related('homemakers').order_by('id')
    return render(request, 'rotation/maintenance_list.html',
                {'maintenance_tasks': maintenance_task, 'create_form': form, 'edit_form': MaintenanceForm()})

@login_required
@require_POST
def maintenance_edit(request):
    pk = request.POST.get("maintenance_id")
    maintenance_task = get_object_or_404(Maintenance, pk=pk)

    form = MaintenanceForm(request.POST, instance=maintenance_task)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.save()
        form.save_m2m()
        return redirect('rotation:maintenance_list')

    maintenance_tasks = Maintenance.objects.prefetch_related('homemakers').order_by('id')
    return render(
        request,
        'rotation/maintenance_list.html',
        {'maintenance_tasks': maintenance_tasks, 'create_form': MaintenanceForm(), 'edit_form': form}
    )

@login_required
@require_POST
def maintenance_delete(request):
    pk = request.POST.get("maintenance_id")
    maintenance_task = get_object_or_404(Maintenance, pk=pk)
    maintenance_task.delete()
    return redirect('rotation:maintenance_list')