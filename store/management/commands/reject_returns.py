from django.core.management.base import BaseCommand

from store.models import ReturnPurchase


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        ReturnPurchase.objects.all().delete()
