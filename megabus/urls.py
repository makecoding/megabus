from django.urls import path
from . import views

urlpatterns = [
    #(실제 root이하의 web url (html 파일 위치가 아님), views.py의 메서드, ??)
    # http://127.0.0.1:8000/megabus/
    path('', views.index, name='index'),

    path('member/joinform', views.joinform, name='joinform'),
    path('member/join', views.join, name='join'),

    path('member/loginform', views.loginform, name='loginform'),
    path('member/login', views.login, name='login'),
    path('member/logout', views.logout, name='logout'),

    path('takeonoff/busform', views.busform, name='busform'),
    path('takeonoff/stopform', views.stopform, name='stopform'),

    path('pay/prepayform', views.prepayform, name='prepayform'),
    path('pay/prepay', views.prepay, name='prepay'),

    path('mypage/mypage', views.mypage, name='mypage'),
    path('mypage/uselist', views.uselist, name='uselist'),
    path('mypage/paylist', views.paylist, name='paylist'),
    path('mypage/mileagelist', views.mileagelist, name='mileagelist'),



    #bus 관련


]
