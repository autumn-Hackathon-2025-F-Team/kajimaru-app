import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from .models import ShoppingItem
from .forms import ShoppingAddForm
from apps.user.models import Household, Users
from apps.user.views import HK, MK
from django.contrib import messages
from django.urls import reverse

def _current_household(request):
    hh_id =request.session.get(HK)
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
    items = (ShoppingItem.objects.filter(household=hh, is_purchased=False).select_related('added_by', 'purchased_by').order_by('-created_at'))
    bought = (ShoppingItem.objects.filter(household=hh, is_purchased=True).select_related('added_by', 'purchased_by').order_by('-purchased_at')[:30])

    form = ShoppingAddForm()
    return render(request, 'shopping/shopping_list.html', {'items': items, 'bought': bought, 'form': form})

@login_required
@require_POST
def add(request):
    hh = _current_household(request)
    if not hh:
        return JsonResponse({'ok': False, 'error': 'no_household'}, status=400)
    
    form = ShoppingAddForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors.get_json_data()}, status=400)
    
    kwargs = dict(
        household = hh,
        item_name=form.cleaned_data['item_name'].strip(),
        quantity=form.cleaned_data['quantity'],
        description=(form.cleaned_data.get('description') or '').strip(),
    )
    user_id = request.session.get(MK)

    if hasattr(ShoppingItem, 'added_by'):
        kwargs['added_by_id'] = user_id
    elif hasattr(ShoppingItem, 'buyer'):
        kwargs['buyer_id'] = user_id
    
    item = ShoppingItem.objects.create(**kwargs)
    
    html = render_to_string('shopping/partials/item.html', {'it': item}, request=request)
    return JsonResponse({'ok': True, 'html': html})

@login_required
@require_POST
def toggle(request, pk: int):
    hh = _current_household(request)
    it = get_object_or_404(ShoppingItem, id=pk, household=hh)

    it.is_purchased = not it.is_purchased
    if it.is_purchased:
        it.purchased_at = timezone.now()
        it.purchased_by = Users.objects.filter(id=request.session.get(MK)).first()
    else:
        it.purchased_at = None
        it.purchased_by = None
    it.save()

    html = render_to_string('shopping/partials/item.html', {'it': it}, request=request)
    return JsonResponse({'ok': True, 'html': html, 'purchased': it.is_purchased, 'id': it.id})

@login_required
def detail(request, pk: int):
    hh = _current_household(request)
    it = get_object_or_404(
        ShoppingItem.objects.select_related('added_by', 'purchased_by'),
        id=pk, household=hh
    )

    # 互換: 旧モデル(buyer)も拾う
    adder = getattr(it, "added_by", None) or getattr(it, "buyer", None)
    purchaser = getattr(it, "purchased_by", None)

    def name_of(u):
        if not u:
            return None
        # nickname が空なら display_name をフォールバック
        return getattr(u, "nickname", None) or getattr(u, "display_name", None) or str(u)

    ctx = {
        "it": it,
        "added_name": name_of(adder),
        "purchased_name": name_of(purchaser) if it.is_purchased else None,
    }
    html = render_to_string("shopping/partials/detail.html", ctx, request=request)
    return JsonResponse({"ok": True, "html": html})

@login_required
@require_POST
def delete(request, pk:int):
    hh = _current_household(request)
    it = get_object_or_404(ShoppingItem, id=pk, household=hh)
    it.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'id': pk})

    messages.success(request, '削除しました。')
    next_url = request.POST.get('next') or reverse('shopping:list')
    return redirect(next_url)


