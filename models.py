import datetime

from django.db import models

from django.contrib.auth.models import User


class PendingGame(models.Model):
    owner = models.ForeignKey(User, related_name="owner")
    joiner = models.ForeignKey(User, related_name="joiner", null=True)
    date_created = models.DateTimeField("date_created")
    game_name = models.CharField(max_length=200)

    def __str__(self):
        return self.game_name

    @classmethod
    def create(cls, name, owner):
        pg = cls(owner=owner, game_name=name, date_created=datetime.datetime.now())
        pg.save()
        return pg

    def startGame(self):
        self.delete()
        return 0

    def join(self, user):
        self.joiner = user
        self.save()

    def isFull(self):
        return self.owner is not None and self.joiner is not None

    @classmethod
    def get(cls, gid):
        return cls.objects.get(id=gid)
