from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import datetime

from apps.user.views import HK
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


