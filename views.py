# Create your views here.

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.decorators import login_required

def Index(request):
    if not request.user.is_authenticated():
        params_dict = {'user': None}
    else:
        params_dict = {'user': request.user}

    # Get the list of pending games
    pending_games = PendingGame.objects.order_by('-date_created')
    params_dict['pending_games'] = pending_games
    if request.user.is_authenticated and _canCreate(request.user):
        params_dict['can_create'] = '1'

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
            return render(request, 'rebellion/create_account.html')
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
        print(request.user, pg.joiner, pg.isFull(), request.user.is_authenticated)
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
            game_id = pg.startGame()
            print("Created !")  # TODO
            # return HttpResponseRedirect(reverse('rebellion:view_game', kwargs={'game_id': pg.id}))
            return HttpResponseRedirect(reverse('rebellion:index'))
        else:
            return HttpResponseRedirect(reverse('rebellion:index'))
    return HttpResponseRedirect(reverse('rebellion:index'))

@login_required
def JoinGame(request):
    if request.method == 'POST' :
        pg = PendingGame.get(request.POST['pgame_id'])
        if pg.owner is not None and pg.owner != request.user and not pg.isFull():
            pg.join(request.user)
            return HttpResponseRedirect(reverse('rebellion:pending_game', kwargs={'pgame_id': pg.id}))
    return HttpResponseRedirect(reverse('rebellion:index'))


def ViewGame(request, game_id):
    return HttpResponseRedirect(reverse('rebellion:index'))
