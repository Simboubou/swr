import datetime

from django.db import models

from django.contrib.auth.models import User
from random import random


class PendingGame(models.Model):
    owner = models.ForeignKey(User, related_name="owned_game")
    joiner = models.ForeignKey(User, related_name="joined_game", null=True)
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
        r = random()
        if r > 0.5:
            g = Game.create(self.game_name, self.owner, self.joiner)
        else:
            g = Game.create(self.game_name, self.joiner, self.owner)
        self.delete()
        return g

    def join(self, user):
        self.joiner = user
        self.save()

    def isFull(self):
        return self.owner is not None and self.joiner is not None

    @classmethod
    def get(cls, gid):
        return cls.objects.get(id=gid)


class Game(models.Model):
    rebel_player = models.ForeignKey(User, related_name="playing_rebel")
    imperial_player = models.ForeignKey(User, related_name="playing_imperial", null=True)
    date_created = models.DateTimeField("date_created")
    game_name = models.CharField(max_length=200)

    turn = models.IntegerField(default=1)
    time_marker = models.IntegerField(default=1)
    reputation_marker = models.IntegerField(default=14)

    def __str__(self):
        return self.game_name

    @classmethod
    def create(cls, name, rebel, imp):
        pg = cls(rebel_player=rebel, imperial_player=imp, game_name=name, date_created=datetime.datetime.now())
        pg.time_marker = 1
        pg.reputation_marker = 14
        pg.turn = 1
        pg.save()
        return pg

    @classmethod
    def get(cls, gid):
        return cls.objects.get(id=gid)
