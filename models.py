import datetime

from django.db import models
from django.template import loader
from django.contrib.auth.models import User
from random import random

from .global_params import *


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

    turn = models.PositiveSmallIntegerField(default=1)
    time_marker = models.PositiveSmallIntegerField(default=1)
    reputation_marker = models.PositiveSmallIntegerField(default=14)

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


class System(models.Model):
    name = models.CharField(max_length=100)
    isPopulous = models.BooleanField(default=False)
    prodRank = models.PositiveSmallIntegerField(default=1)
    prod1isGround = models.BooleanField(default=True)
    prod2isGround = models.BooleanField(default=True)
    prod1level = models.PositiveSmallIntegerField(default=0)
    prod2level = models.PositiveSmallIntegerField(default=0)

    @classmethod
    def create(cls,**kwargs) :
        s = cls(**kwargs)
        s.save()
        return s

    def __str__(self):
        return self.name

class SystemLink(models.Model):
    origin = models.ForeignKey(System, related_name="neighbours")
    dest = models.ForeignKey(System)

    @classmethod
    def createSym(cls, system1, system2):
        link = cls(origin=system1, dest=system2)
        link.save()
        link = cls(origin=system2, dest=system1)
        link.save()



class SystemInstance(models.Model):
    game = models.ForeignKey(Game)
    system = models.ForeignKey(System)
    loyalty = models.SmallIntegerField(default=0)  # -1 for imperial, 1 for rebel
    isSubjugated = models.BooleanField(default=False)
    isSabotaged = models.BooleanField(default=False)

    nbXwings = models.SmallIntegerField(default=0)
    nbYwings = models.SmallIntegerField(default=0)
    nbRtransports = models.SmallIntegerField(default=0)
    nbCorvettes = models.SmallIntegerField(default=0)
    nbMonCals = models.SmallIntegerField(default=0)
    nbCorvettes = models.SmallIntegerField(default=0)

    nbTies = models.SmallIntegerField(default=0)
    nbCarriers = models.SmallIntegerField(default=0)
    nbDestroyers = models.SmallIntegerField(default=0)

    nbSSD = models.SmallIntegerField(default=0)
    nbDStars = models.SmallIntegerField(default=0)
    nbDSUCs = models.SmallIntegerField(default=0)

    nbTroops = models.SmallIntegerField(default=0)
    nbSpeeders = models.SmallIntegerField(default=0)
    nbShields = models.SmallIntegerField(default=0)
    nbIons = models.SmallIntegerField(default=0)

    nbStorms = models.SmallIntegerField(default=0)
    nbATSTs = models.SmallIntegerField(default=0)
    nbATATs = models.SmallIntegerField(default=0)

    def render(self):
        template = loader.get_template('rebellion/single_system.html')
        sys = self.system
        p = {}
        p['name'] = sys.name
        p['isPopulous'] = sys.isPopulous
        if p['isPopulous']:
            p['loyalty'] = (['I', 'N', 'R'])[self.loyalty + 1]
            if p['loyalty'] == 'I':
                p['loyalty_color'] = RebellionParams.colors['Empire']
            elif p['loyalty'] == 'N':
                p['loyalty_color'] = RebellionParams.colors['White']
            else:
                p['loyalty_color'] = RebellionParams.colors['Rebel']
            p['prodrank'] = sys.prodRank
            p['prod1style'] = RebellionParams.colors['GroundProd' if self.system.prod1isGround else 'SpaceProd']
            p['prod2style'] = RebellionParams.colors['GroundProd' if self.system.prod2isGround else 'SpaceProd']
            p['prod1level'] = sys.prod1level
            if sys.prod2level > 0:
                p['prod2level'] = sys.prod2level

        if self.nbXwings > 0:
            p['X'] = self.nbXwings
        if self.nbYwings > 0:
            p['Y'] = self.nbYwings
        if self.nbRtransports > 0:
            p['T'] = self.nbRtransports
        if self.nbCorvettes > 0:
            p['C'] = self.nbCorvettes
        if self.nbMonCals > 0:
            p['M'] = self.nbMonCals

        if self.nbTies > 0:
            p['TF'] = self.nbTies
        if self.nbCarriers > 0:
            p['AC'] = self.nbCarriers
        if self.nbDestroyers > 0:
            p['D'] = self.nbDestroyers
        if self.nbSSD > 0:
            p['I'] = self.nbSSD
        if self.nbDStars > 0:
            p['O'] = self.nbDStars
        if self.nbDSUCs > 0:
            p['G'] = self.nbDSUCs

        if self.nbTroops > 0:
            p['RT'] = self.nbTroops
        if self.nbSpeeders > 0:
            p['S'] = self.nbSpeeders
        if self.nbShields > 0:
            p['SG'] = self.nbShields
        if self.nbIons > 0:
            p['IC'] = self.nbIons

        if self.nbStorms > 0:
            p['ST'] = self.nbStorms
        if self.nbATSTs > 0:
            p['ATST'] = self.nbATSTs
        if self.nbATATs > 0:
            p['ATAT'] = self.nbATATs

        return template.render(p, None)


class Leader(models.Model):
    name = models.CharField(max_length=100)
    isRebel = models.BooleanField(default=False)
    isGround = models.BooleanField(default=False)
    groundTactic = models.PositiveSmallIntegerField(default=1)
    spaceTactic = models.PositiveSmallIntegerField(default=1)
    diploLevel = models.PositiveSmallIntegerField(default=1)
    intelLevel = models.PositiveSmallIntegerField(default=1)
    opsLevel = models.PositiveSmallIntegerField(default=1)
    logLevel = models.PositiveSmallIntegerField(default=1)


class LeaderInstance(models.Model):
    game = models.ForeignKey(Game)
    leader = models.ForeignKey(Leader)
    ring = models.CharField(max_length=12)
    system = models.ForeignKey(System, null=True)
    isInPlay = models.BooleanField(default=False)
