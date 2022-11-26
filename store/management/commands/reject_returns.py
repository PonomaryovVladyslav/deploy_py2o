from django.core.management.base import BaseCommand

from store.models import ReturnPurchase


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        returns = ReturnPurchase.objects.all()
        if returns:
            returns.delete()
            self.stdout.write('All return requests have been deleted')
        else:
            self.stdout.write('Return requests not found')
