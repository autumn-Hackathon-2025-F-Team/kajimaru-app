from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
import datetime

from apps.user.views import HK, MK
from apps.user.models import Household, Users
from apps.shopping.models import ShoppingItem
from .models import StockItem
from .forms import StockForm

def _current_household(request):
    hh_id = request.session.get(HK)
    if not hh_id and request.user.is_authenticated:
        from apps.user.models import Household
        return Household.objects.filter(owner=request.user).first()
    from apps.user.models import Household
    return Household.objects.filter(id=hh_id).first()

@login_required
def list_view(request):
    hh = _current_household(request)
    if not hh:
        return redirect('welcome')
    items = StockItem.objects.filter(household=hh).order_by('category', 'stock_name')
    return render(request, 'stocks/stock_management.html', {'items': items})

@login_required
def create_view(request):
    hh = _current_household(request)
    if not hh:
        messages.error(request, '世帯情報がみつかりません。')
        return redirect('welcome')
    
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.household = hh
            item.remind_at = timezone.make_aware(
                datetime.datetime.combine(item.purchase_date, datetime.time.min)
            ) + datetime.timedelta(days=item.period_days - 2)
            item.save()
            messages.success(request, '在庫を登録しました。')
            return redirect('stocks:list')
    else:
        form = StockForm()
    return render(request, 'stocks/list.html', {'form': form})


@login_required
@require_POST
def enqueue_due_to_shopping(request):
    hh = _current_household(request)
    if not hh:
        return redirect('welcome')
    
    due_items = StockItem.objects.filter(
        household = hh,
        remind_at__lte=timezone.now(),
        enqueued_to_shopping = False
    )

    added = 0
    active_member_id = request.session.get(MK)

    for s in due_items:
        exists = ShoppingItem.objects.filter(
            household = hh,
            item_name = s.stock_name,
            is_purchased = False,
        ).exists()
        if exists:
            s.enqueued_to_shopping = True
            s.save(update_fields=['enqueued_to_shopping'])
            continue

        kwargs = dict(
            household = hh,
            item_name = s.stock_name,
            quantity = max(1, s.quantity),
            description = '在庫ハブからの自動追加（期限間近）',
        )

        if hasattr(ShoppingItem, 'added_by_id'):
            kwargs['added_by_id'] = active_member_id
        elif hasattr(ShoppingItem, 'buyer_id'):
            kwargs['buyer_id'] = active_member_id
        
        ShoppingItem.objects.create(**kwargs)
        s.enqueued_to_shopping = True
        s.save(update_fields=['enqueued_to_shopping'])
        added += 1
    
    if request.headers.get('HX-Requested-With') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'added': added})
    
    messages.success(request, f'買い物リストへ {added} 件を追加しました。')
    return redirect(reverse('stocks:list'))

@login_required
@require_POST
def delete(request, pk:int):
    hh = _current_household(request)
    item = get_object_or_404(StockItem, id=pk, household=hh)
    item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'id': pk})
    
    messages.success(request, '削除しました。')
    return redirect('stocks:list')
