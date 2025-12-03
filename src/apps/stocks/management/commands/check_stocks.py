from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from apps.stocks.models import StockItem
from apps.shopping.models import ShoppingItem
from apps.user.models import Users

class Command(BaseCommand):
    help = "期限が近い在庫を買い物リストへ自動追加する（2日前）"

    def handle(self, *args, **options):
        now = timezone.now()
        due_qs = StockItem.objects.select_related("household").filter(remind_at__lte=now)

        created = 0
        for s in due_qs:
            # すでに未購入の ShoppingItem を紐付け済みならスキップ
            if s.open_shopping_item and not s.open_shopping_item.is_purchased:
                continue

            with transaction.atomic():
                item = ShoppingItem.objects.create(
                    household=s.household,
                    item_name=s.stock_name,
                    quantity=max(1, s.quantity),
                    description=f"在庫から自動追加（{s.get_category_display()} / 目安 {s.period_days}日）",
                    is_purchased=False,
                )
                s.open_shopping_item = item
                s.save(update_fields=["open_shopping_item"])
                created += 1

        self.stdout.write(self.style.SUCCESS(f"自動追加: {created} 件"))
