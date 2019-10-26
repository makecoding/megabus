from django.urls import path
from . import views

urlpatterns = [
    # REST 제공용
    # 앱 로그인 요청
    path('api/login', views.GetLoginID.as_view(), name='apilogin'),
    # 앱 mid 요청
    path('api/getMid', views.GetMid.as_view(), name='getMid'),
    # 앱 승하차 알림 (등록버스 정류장 도착여부)요청
    path('api/noitOnOff', views.NotiOnOff.as_view(), name='noitOnOff'),
    # 앱 사용자 상태 요청
    path('api/getStatus', views.GetStatus.as_view(), name='getStatus'),

    # 앱 버스 승차 처리
    path('api/bus_getOn', views.GetOn.as_view(), name='getOn'),
    # 앱 정류장 검색 처리
    path('api/searchStation', views.SearchStation.as_view(), name='getStation'),
    # 앱 최신 사용자 상태 요청
    path('api/getcInfo', views.GetCurrentInfo.as_view(), name='getCInfo'),

    path('bussys/bus_getInfo', views.GetBusInfo.as_view(), name='bus_getInfo'),

    #(실제 root이하의 web url (html 파일 위치가 아님), views.py의 메서드, ??)
    # http:/127.0.0.1:8000/megabus/
    # 메인페이지
    path('', views.index, name='index'),
    # 앱용 메인 페이지
    path('mindex', views.mindex, name='mindex'),
    # 결과 알림 페이지
    path('notice', views.notice, name='notice'),

    # 회원가입 신청 페이지
    path('member/joinform', views.joinform, name='joinform'),
    # 회원가입 처리
    path('member/join', views.join, name='join'),

    # 로그인 입력 페이지
    path('member/loginform', views.loginform, name='loginform'),
    # 로그인 처리
    path('member/login', views.login, name='login'),
    # 로그아웃 처리
    path('member/logout', views.logout, name='logout'),

    # 버스번호 선택 입력 페이지
    path('takeonoff/busform', views.busform, name='busform'),
    # 정류장 선택 입력 페이지
    path('takeonoff/stopform', views.stopform, name='stopform'),

    # 선결제 입력 페이지
    path('pay/prepayform', views.prepayform, name='prepayform'),
    # 버스번호/승하차정류장/선결제 처리
    path('pay/prepay', views.prepay, name='prepay'),

    # 승차대기 선택 페이지
    path('takeonoff/readyform', views.readyform, name='readyform'),
    # 승차대기 처리
    path('takeonoff/ready', views.ready, name='ready'),

    # 승하차 QR코드 생생 페이지
    path('qr/makeqr', views.makeqr, name='makeqr'),

    # 마이페이지 메인
    path('mypage/mypage', views.mypage, name='mypage'),
    # 마이페이지 이용내역
    path('mypage/uselist', views.uselist, name='uselist'),
    # 마이페이지 결제내역
    path('mypage/paylist', views.paylist, name='paylist'),
    # 마이페이지 마일리지 내역
    path('mypage/mileagelist', views.mileagelist, name='mileagelist'),
    # 마이페이지 즐겨찾기 등록 처리
    path('mypage/bookmark', views.bookmark, name='bookmark'),

    # 하차 태깅용
    path('getoff/bus_getoff', views.bus_getoff, name='bus_getoff'),


    # 버스 단말기용 urls
    # 버스용 qt태그 페이지
    path('bussys/bus_makeqr', views.bus_makeqr, name='bus_makeqr'),



    #bus 관련


]
