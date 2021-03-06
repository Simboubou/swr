# Create your views here.

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.decorators import login_required


def Index(request):
    params_dict = {}

    # Get the list of pending games
    pending_games = PendingGame.objects.order_by('-date_created')
    params_dict['pending_games'] = pending_games
    if request.user.is_authenticated and _canCreate(request.user):
        params_dict['can_create'] = '1'

    # Get the list of ongoing games
    ongoing_games = Game.objects.order_by('-date_created')
    params_dict['ongoing_games'] = ongoing_games

    return render(request, 'rebellion/index.html', params_dict)


def _canCreate(user):
    if not user.is_authenticated:
        return False
    return len(PendingGame.objects.filter(owner=user)) == 0


def Login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('rebellion:index'))
    else:
        return HttpResponseRedirect(reverse('rebellion:index'))


def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('rebellion:index'))


def CreateAccount(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('rebellion:index'))
        else:
            return render(request, 'rebellion/create_account.html', )
    elif request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, email=email, password=password1)
                user = authenticate(request, username=username, password=password1)
                if user is not None:
                    login(request, user)
                return HttpResponseRedirect(reverse('rebellion:index'))
            else:
                return HttpResponseRedirect(
                    reverse('rebellion:index'))
    return HttpResponseRedirect(reverse('rebellion:index'))


def ViewPendingGame(request, pgame_id):
    if request.method == 'GET':
        pg = PendingGame.get(pgame_id)
        params = {'game': pg}
        if request.user == pg.owner:
            if pg.joiner is not None:
                params['can_start'] = '1'
        elif request.user.is_authenticated and not pg.isFull():
            params['can_join'] = '1'
        return render(request, 'rebellion/pending_game.html', params)
    return HttpResponseRedirect(reverse('rebellion:index'))


@login_required
def CreatePendingGame(request):
    if request.method == 'POST':
        if _canCreate(request.user):
            pg = PendingGame.create(request.user.username + '\'s game', request.user)
            return HttpResponseRedirect(reverse('rebellion:pending_game', kwargs={'pgame_id': pg.id}))
        else:
            return HttpResponseRedirect(
                reverse('rebellion:index'))
    return HttpResponseRedirect(reverse('rebellion:index'))


@login_required
def StartGame(request):
    if request.method == 'POST':
        pg = PendingGame.get(request.POST['pgame_id'])
        if pg.owner == request.user and pg.joiner is not None:
            started_game = pg.startGame()
            return HttpResponseRedirect(reverse('rebellion:view_game', kwargs={'game_id': started_game.id}))
        else:
            return HttpResponseRedirect(reverse('rebellion:index'))
    return HttpResponseRedirect(reverse('rebellion:index'))


@login_required
def JoinGame(request):
    if request.method == 'POST':
        pg = PendingGame.get(request.POST['pgame_id'])
        if pg.owner is not None and pg.owner != request.user and not pg.isFull():
            pg.join(request.user)
            return HttpResponseRedirect(reverse('rebellion:pending_game', kwargs={'pgame_id': pg.id}))
    return HttpResponseRedirect(reverse('rebellion:index'))


def ViewGame(request, game_id):
    if request.method == 'GET':
        pg = Game.get(game_id)
        params = {'game': pg}
        sys = System(name="Coruscant", isPopulous=True, prod1level=2, prod1isGround=True, prod2level=1,
                     prod2isGround=False, prodRank=1)
        sys.save()
        sysIns = SystemInstance(system=sys, game=pg, loyalty=-1)
        sysIns.nbXwings = 2
        sysIns.nbYwings = 5
        sysIns.nbMonCals = 2
        sysIns.nbStorms = 5
        sysIns.nbATSTs = 1
        sysIns.nbRtransports = 0
        sysIns.save()
        params['test'] = sysIns.render()
        sysIns.delete()
        sys.delete()
        return render(request, 'rebellion/game.html', params)
