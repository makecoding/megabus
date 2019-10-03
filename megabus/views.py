from django.db import connection
from django.shortcuts import render

from urllib.parse import *
from urllib.request import *

from django.http import HttpResponse
from django.template import loader

import requests
from bs4 import BeautifulSoup

def index(request):
    mid = 0
    if request.session.has_key('mid'):
        mid = request.session['mid']
    print("index mid : "+str(mid))
    return render(request, 'main.html', {'mid': mid})

def joinform(request):
    return render(request, 'member/join.html')

def join(request):
    uid = request.POST['uid']
    uname = request.POST['uname']
    uphone = request.POST['uphone']
    upw1 = request.POST['upw1']
    disabled = request.POST['disabled']

    # 회원 가입
    query = "insert into megabus_member(id,name,upw,phonenumber,handicap,mileage)  " \
            "values('%s','%s','%s','%s','%s',1000)" % (uid, uname, upw1, uphone, disabled)
    cursor = connection.cursor()
    cursor.execute(query)

    query = "select mid from megabus_member where id='%s' and upw='%s';" % (uid, upw1)
    cursor = connection.cursor()
    row = cursor.execute(query)
    mid = row.fetchone()[0]

    # 가입 마일리지 적립
    query = "insert into megabus_mileage(mid,cretype,creamt,crewhere)  " \
            "values('%s','적립','1000','가입')" % (mid)
    cursor = connection.cursor()
    cursor.execute(query)

    return render(request, 'member/login.html')

def loginform(request):
    return render(request, 'member/login.html')

def login(request):
    uid = request.POST['uid']
    upw = request.POST['upw']

    query = "select mid from megabus_member where id='%s' and upw='%s';" % (uid, upw)

    cursor = connection.cursor()
    row = cursor.execute(query)
    rst = row.fetchone()[0]

    if rst:
        mid = rst
        request.session['mid'] =mid

        print("로그인 성공!!!")
        return render(request, 'main.html', {'mid': mid})
    else:
        print("로그인 실패!!!")
        return render(request, 'member/login.html')

def logout(request):
    mid = 0
    try:
        del request.session['mid']
    except:
        pass
    return render(request, 'main.html', {'mid': mid})

def busform(request):
    busdic = []
    print(len(request.POST))
    if len(request.POST)>0:
        busnum = request.POST['busnum']

        # 검색어로 버스번호 조회 openAPI 연동 REST [XML]
        url = 'http://ws.bus.go.kr/api/rest/busRouteInfo/getBusRouteList'
        keystr = '?serviceKey=WS6IE%2F0nHkArdmPt3284YdVVLGtZPSuSQ0ANuFo463Hj3KU9zb7RpSz5hJHWQpWw0sE0Vbz9V4f7zBSdO7%2FR1A%3D%3D'
        param1 = '&strSrch='+busnum

        response = requests.get(url+keystr+param1)
        soup = BeautifulSoup(response.text, 'html.parser')

        # soup의 모든 node는 소문자
        idlist =  soup.findAll('busrouteid')
        numList = soup.findAll('busroutenm')

        for i, val in enumerate(numList):
            busdic.append([idlist[i].text, numList[i].text])

        return render(request, 'takeonoff/bus.html', {'busdic':busdic})
    else:
        return render(request, 'takeonoff/bus.html')

def stopform(request):
    rst = []

    bnum = request.POST['bnum']
    print("stopform bnum:"+bnum)
    brid = request.POST['brid']
    print("stopform brid:"+brid)

    # 선택버스의 노선조회 openAPI 연동 REST [XML]
    url = 'http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute'
    keystr = '?serviceKey=WS6IE%2F0nHkArdmPt3284YdVVLGtZPSuSQ0ANuFo463Hj3KU9zb7RpSz5hJHWQpWw0sE0Vbz9V4f7zBSdO7%2FR1A%3D%3D'
    param1 = '&busRouteId='+brid

    response = requests.get(url+keystr+param1)
    soup = BeautifulSoup(response.text, 'html.parser')

    # soup의 모든 node는 소문자
    idlist = soup.findAll('station')
    nameList = soup.findAll('stationnm')
    goallst = soup.findAll('direction')

    for i, val in enumerate(nameList):
        rst.append([idlist[i].text, nameList[i].text, goallst[i].text])

    return render(request, 'takeonoff/onoffstop.html',{'stationlst':rst,'bnum':bnum})

def prepayform(request):
    bnum = request.POST['bnum']
    print("prepayform bnum:" + bnum)
    onstation = request.POST['onstation']
    offstation = request.POST['offstation']

    mid = request.session['mid']
    print("prepayform mid:" + str(mid))
    if mid>0:
        # 사용자 보유 마일리지 조회
        query = "select sum(creamt) from megabus_mileage where mid='%s';" % mid
        print(query)
        cursor = connection.cursor()
        row = cursor.execute(query)
        mileage = row.fetchone()[0]

        dic = {'mid': mid,"onstation":onstation,"offstation":offstation,'bnum':bnum, 'mileage':mileage}

        return render(request, 'pay/prepay.html', dic)
    else:

        return render(request, 'member/login.html')

def prepay(request):
    bnum = request.POST['bnum']
    print("prepay bnum:" + bnum)
    onbsid = request.POST['onbsid']
    onbsname = request.POST['onbsname']
    offbsid = request.POST['offbsid']
    offbsname = request.POST['offbsname']
    payamt = request.POST['payamt']
    paytype = request.POST['paytype']

    mid = request.session['mid']
    # 승하차 등록 내역 저장
    query = "insert into megabus_uselist (mid, bnid, onbsid, onbsname, offbsid, offbsname, pid, payamt)" \
            "  values(%d, '%s', '%s','%s', '%s','%s', '%s', '%s')" % (int(mid), bnum, onbsid, onbsname, offbsid, offbsname,paytype, payamt)
    print(query)
    cursor = connection.cursor()
    cursor.execute(query)

    # 승하차 등록시 마일리지 차감
    query = "insert into megabus_mileage (mid, cretype, creamt, crewhere)" \
            "  values(%d, '사용', %d, '승하차등록')" % (int(mid), -100)
    print(query)
    cursor = connection.cursor()
    cursor.execute(query)

    # 선결제 진행
    if paytype != '':
        query = "insert into megabus_mileage (mid, cretype, creamt, crewhere)" \
                "  values(%d, '적립', %d, '선결제')" % (int(mid), 0.03 * int(payamt))
        print(query)
        cursor = connection.cursor()
        cursor.execute(query)
        # 마일리지 결제
        if paytype=='3':
            query = "insert into megabus_mileage (mid, cretype, creamt, crewhere)" \
                    "  values(%d, '사용', %d, '선결제')" % (int(mid), -1*int(payamt))
            print(query)
            cursor = connection.cursor()
            cursor.execute(query)

    return render(request, 'main.html')

def mypage(request):
    mid = request.session['mid']
    print("mypage mid:" + str(mid))

    # 사용자 보유 마일리지 조회
    query = "select sum(creamt) from megabus_mileage where mid='%s';" % mid
    print(query)
    cursor = connection.cursor()
    row = cursor.execute(query)
    mileage = row.fetchone()[0]

    if mid > 0:
        dic = {'mid': mid, 'mileage': mileage}

        return render(request, 'mypage/mypage.html', dic)
    else:

        return render(request, 'member/login.html')

def uselist(request):
    mid = request.session['mid']
    print("uselist mid:" + str(mid))

    if mid > 0:
        # 버스노선 이용내역
        query = "select ulid, bnid, onbsname, offbsname, usedate from megabus_uselist " \
                "where mid=%d order by usedate desc;" % int(mid)
        print(query)
        cursor = connection.cursor()
        row = cursor.execute(query)
        rst = row.fetchall()

        dic = {'mid': mid, 'rstlst': rst}

        return render(request, 'mypage/uselist.html', dic)
    else:

        return render(request, 'member/login.html')

def paylist(request):
    mid = request.session['mid']
    print("mypage mid:" + str(mid))

    # 사용자 보유 마일리지 조회
    query = "select sum(creamt) from megabus_mileage where mid='%s';" % mid
    print(query)
    cursor = connection.cursor()
    row = cursor.execute(query)
    mileage = row.fetchone()[0]

    if mid > 0:
        dic = {'mid': mid, 'mileage': mileage}

        return render(request, 'mypage/mypage.html', dic)
    else:

        return render(request, 'member/login.html')

def mileagelist(request):
    mid = request.session['mid']
    print("mypage mid:" + str(mid))

    # 사용자 보유 마일리지 조회
    query = "select sum(creamt) from megabus_mileage where mid='%s';" % mid
    print(query)
    cursor = connection.cursor()
    row = cursor.execute(query)
    mileage = row.fetchone()[0]

    if mid > 0:
        dic = {'mid': mid, 'mileage': mileage}

        return render(request, 'mypage/mypage.html', dic)
    else:

        return render(request, 'member/login.html')

