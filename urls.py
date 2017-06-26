from django.conf.urls import url

from . import views

app_name = 'rebellion'
urlpatterns = [
    url(r'^$', views.Index, name='index'),
    url(r'^login/$', views.Login, name="login"),
    url(r'^logout/$', views.Logout, name="logout"),
    url(r'^create_account/$', views.CreateAccount, name="create_account"),
    url(r'^pending_game/(?P<pgame_id>[0-9]+)$', views.ViewPendingGame, name="pending_game"),
    url(r'^create_pending_game/$', views.CreatePendingGame, name="create_pending_game"),
    url(r'^start_game/$', views.StartGame, name="start_game"),
    url(r'^join_game/$', views.JoinGame, name="join_game"),
    url(r'^view_game/(?P<game_id>[0-9]+)$', views.ViewGame, name="view_game")
]
