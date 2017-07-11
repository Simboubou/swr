from django.core.management.base import BaseCommand, CommandError
from ...models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        System.objects.all().delete()
        SystemLink.objects.all().delete()

        dathomir = System.create(name="Dathomir", isPopulous=False)
        mandalore = System.create(name="Mandalore", isPopulous=True, prod1level=1, prod1isGround=True, prod2level=1,
                                  prod2isGround=False, prodRank=1)
        kashyyyk = System.create(name="Kashyyyk", isPopulous=True, prod1level=1, prod1isGround=True, prod2level=1,
                                 prod2isGround=True, prodRank=1)
        malastare = System.create(name="Malastare", isPopulous=True, prod1level=1, prod1isGround=True, prodRank=1)

        SystemLink.createSym(dathomir, mandalore)
        SystemLink.createSym(mandalore, kashyyyk)
        SystemLink.createSym(kashyyyk, malastare)
