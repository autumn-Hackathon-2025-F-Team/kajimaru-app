from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from apps.user.views import HK
from apps.user.models import Household
from .models import MaintenanceItem
from .forms import MaintenanceCreateForm, MaintenanceDeleteForm

def _current_household(request):
    hh_id = request.session.get(HK)
    if hh_id:
        return Household.objects.filter(id=hh_id).first()
    if request.user.is_authenticated:
        return Household.objects.filter(owner=request.user).first()
    return None

@login_required
def list_view(request):
    hh = _current_household(request)
    if not hh:
        return redirect('welcome')
    
    appliances = MaintenanceItem.objects.filter(household=hh, is_appliance=True).order_by('next_date')
    facilities = MaintenanceItem.objects.filter(household=hh, is_appliance=False).order_by('next_date')

    add_form = MaintenanceCreateForm()
    del_form = MaintenanceDeleteForm()
    del_form.fields['item_id'].widget.choices = [
        (m.id, f'{"家電" if m.is_appliance else "設備"}: {m.target_name}（次回 {m.next_date:%Y/%m/%d}）')
        for m in MaintenanceItem.objects.filter(household=hh).order_by('is_appliance', 'target_name')
    ]

    ctx = dict(appliances=appliances, facilities=facilities, add_form=add_form, del_form=del_form)
    return render(request, 'maintenance/maintenance_list.html', ctx)

@login_required
def create_item(request):
    hh = _current_household(request)
    if request.method != "POST":
        return redirect("maintenance:list")
    form = MaintenanceCreateForm(request.POST)
    if not form.is_valid():
        messages.error(request, "入力内容に誤りがあります。")
        return redirect("maintenance:list")

    item: MaintenanceItem = form.save(commit=False)
    item.household = hh
    # next_date / task_date は save() 内で自動算出
    item.save()
    messages.success(request, "メンテナンス項目を追加しました。")
    return redirect("maintenance:list")

@login_required
def delete_item(request):
    hh = _current_household(request)
    if request.method != "POST":
        return redirect("maintenance:list")
    item_id = request.POST.get("item_id")
    item = get_object_or_404(MaintenanceItem, id=item_id, household=hh)
    item.delete()
    messages.success(request, "削除しました。")
    return redirect("maintenance:list")