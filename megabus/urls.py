from django.urls import path
from . import views

urlpatterns = [
    # REST 제공용
    path('api/login', views.GetLoginID.as_view(), name='apilogin'),
    path('api/getMid', views.GetMid.as_view(), name='getMid'),
    path('api/getStatus', views.GetStatus.as_view(), name='getStatus'),

    #(실제 root이하의 web url (html 파일 위치가 아님), views.py의 메서드, ??)
    # http:/127.0.0.1:8000/megabus/
    path('', views.index, name='index'),

    path('notice', views.notice, name='notice'),

    path('member/joinform', views.joinform, name='joinform'),
    path('member/join', views.join, name='join'),

    path('member/loginform', views.loginform, name='loginform'),
    path('member/login', views.login, name='login'),
    path('member/logout', views.logout, name='logout'),

    path('takeonoff/busform', views.busform, name='busform'),
    path('takeonoff/stopform', views.stopform, name='stopform'),

    path('pay/prepayform', views.prepayform, name='prepayform'),
    path('pay/prepay', views.prepay, name='prepay'),

    path('takeonoff/readyform', views.readyform, name='readyform'),
    path('takeonoff/ready', views.ready, name='ready'),

    path('qr/makeqr', views.makeqr, name='makeqr'),

    path('mypage/mypage', views.mypage, name='mypage'),
    path('mypage/uselist', views.uselist, name='uselist'),
    path('mypage/paylist', views.paylist, name='paylist'),
    path('mypage/mileagelist', views.mileagelist, name='mileagelist'),
    path('mypage/bookmark', views.bookmark, name='bookmark'),


    # 버스 단말기용 urls
    path('bussys/bus_geton', views.bus_geton, name='bus_geton'),



    #bus 관련


]
