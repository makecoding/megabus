from django.db import connection
from django.shortcuts import render

import requests
from bs4 import BeautifulSoup

from rest_framework.views import APIView
from rest_framework.response import Response

# API call은 session 사용 불가
class GetLoginID(APIView):
    #DB 사용 example
    def get (self, request, format=None):
        uid = request.GET['uid']
        upw = request.GET['upw']

        query = "select mid from megabus_member where id='%s' and upw='%s';" % (uid, upw)
        cursor = connection.cursor()
        row = cursor.execute(query)
        mid = row.fetchone()

        return Response(mid)

class GetMid(APIView):
    def get (self, request, format=None):

        return Response(request.session['mid'])

class GetStatus(APIView):
    def get (self, request, format=None):

        return Response(request.session['mstatus'])

class GetBusid(APIView):
    def get (self, request, format=None):
        return Response(request.session['vehid'])

class IsArrive(APIView):
    def get(self, request, format=None):

        # 특정노선(예:1000번 버스노선)의 하차 정류장 도착 순서에 따른 차량id 추출 openAPI 연동 REST [XML]
        url = 'http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute'
        keystr = '?serviceKey=WS6IE%2F0nHkArdmPt3284YdVVLGtZPSuSQ0ANuFo463Hj3KU9zb7RpSz5hJHWQpWw0sE0Vbz9V4f7zBSdO7%2FR1A%3D%3D'
        param1 = '&stId=%s&busRouteId=%s&ord=%s' % (
            request.session['offbsid'], request.session['brid'], request.session['offord'])

        print(url + keystr + param1)
        response = requests.get(url + keystr + param1)
        soup = BeautifulSoup(response.text, 'html.parser')

        # soup의 모든 node는 소문자
        vehid1 = soup.find('vehid1').text
        print(vehid1)
        vehid2 = soup.find('vehid2').text
        print(vehid2)
        
        rst = "N"
        # 하차정류장 접근 버스가 현재 탑승버스와 동인한 경우
        if request.session['vehid']==vehid2:
            rst = "Y"

        return Response(rst)

# 공통 알림페이지
def notice(request):

    return render(request, 'notipage.html', {'msg':'하하하하하'})


def mindex(request):
    mid = request.GET["mid"]
    print("mindex mid : " + str(mid))

    request.session['mid'] = mid

    # 사용자 상태에 따라 메인 메뉴 구성 달라짐
    # stat = ''
    # if request.session.has_key('mstatus'):
    #     stat = request.session['mstatus']

    return render(request, 'main.html', {'mid': mid})

def index(request):
    mid = 0
    if request.session.has_key('mid'):
        mid = request.session['mid']
    print("index mid : "+str(mid))
    
    # 사용자 상태에 따라 메인 메뉴 구성 달라짐
    stat = ''
    if request.session.has_key('mstatus'):
        stat = request.session['mstatus']

    return render(request, 'main.html', {'mid': mid, 'stat': stat})

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
        request.session['mid'] = mid

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

# 버스번호 또는 북마크 선택
def busform(request):
    #mid = request.POST['mid']
    mid = request.session['mid']

    print("readyform mid:" + str(mid))

    # bookmark 목록 가져오기
    query = "select ulid, brid, onbsname, offbsname from megabus_uselist " \
            "where mid=%d and bookmark='Y' order by usedate desc;" % int(mid)
    print(query)
    cursor = connection.cursor()
    row = cursor.execute(query)
    rst = row.fetchall()

    busdic = []
    print(len(request.POST))

    #if len(request.POST)>0:
    print(request.POST.keys());
    if 'busnum' in list(request.POST.keys()):
        busnum = request.POST['busnum']
        print("busform busnum:" + busnum)

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

        return render(request, 'takeonoff/bus.html', {'busdic':busdic, 'bookmark':rst})
    else:
        return render(request, 'takeonoff/bus.html', {'bookmark':rst})

# 노선 선택
def stopform(request):
    # 즐겨찾기 선택 안함.
    if 'ulid' not in list(request.POST.keys()):
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
        noList = soup.findAll('stationno')
        goallst = soup.findAll('direction')
        ordlist = soup.findAll('seq')

        rst = []
        for i, val in enumerate(nameList):
            if noList[i].text != "미정차":
                rst.append([idlist[i].text, nameList[i].text, goallst[i].text, ordlist[i].text])

        return render(request, 'takeonoff/onoffstop.html', {'stationlst': rst, 'brid': brid, 'bnum': bnum, 'type':'S'})
    # 즐겨찾기 선택
    else:
        ulid = request.POST['ulid']

        query = "select brid, bnname, onbsid, onbsname, onord, offbsid, offbsname, offord from megabus_uselist where ulid=%d;" % int(ulid)
        print(query)
        cursor = connection.cursor()
        row = cursor.execute(query)
        bookmark = row.fetchone()
        print(bookmark)
        return render(request, 'takeonoff/onoffstop.html', {'bookmark': bookmark, 'type':'B'})



# 선결제 페이지
def prepayform(request):
    brid = request.POST['brid']
    print("prepayform brid:" + brid)
    bnum = request.POST['bnum']
    print("prepayform bnum:" + bnum)
    onbsid = request.POST['onbsid']
    onbsname = request.POST['onbsname']
    onord = request.POST['onord']
    offbsid = request.POST['offbsid']
    offbsname = request.POST['offbsname']
    offord = request.POST['offord']
    alarm = request.POST['alarm']

    mid = request.session['mid']
    print("prepayform mid:" + str(mid))
    if mid>0:
        # 사용자 보유 마일리지 조회
        query = "select sum(creamt) from megabus_mileage where mid='%s';" % mid
        print(query)
        cursor = connection.cursor()
        row = cursor.execute(query)
        mileage = row.fetchone()[0]

        dic = {'mid': mid,"onbsid":onbsid,"onbsname":onbsname,"onord":onord,"offbsid":offbsid,"offbsname":offbsname,"offord":offord,
        'brid':brid,'bnum':bnum, 'mileage':mileage, 'alarm':alarm}

        return render(request, 'pay/prepay.html', dic)
    else:

        return render(request, 'member/login.html')

# 선결제 logic
def prepay(request):
    brid = request.POST['brid']
    bnum = request.POST['bnum']
    onbsid = request.POST['onbsid']
    onbsname = request.POST['onbsname']
    onord = request.POST['onord']
    offbsid = request.POST['offbsid']
    print("prepay offbsid:" + offbsid)
    offbsname = request.POST['offbsname']
    print("prepay offbsname:" + offbsname)
    offord = request.POST['offord']
    print("prepay offord:" + offord)
    payamt = request.POST['payamt']
    paytype = request.POST['paytype']
    alarm = request.POST['alarm']

    mid = request.session['mid']
    # 승하차 등록 내역 저장
    query = "insert into megabus_uselist (mid, brid, bnname, onbsid, onbsname, onord, offbsid, offbsname, offord, pid, payamt, alarm)" \
            "  values (%d, %d, '%s', %d, '%s', %d, %d, '%s', %d, '%s', '%s', '%s')"\
            % (int(mid), int(brid), bnum, int(onbsid), onbsname, int(onord), int(offbsid), offbsname, int(offord), paytype, payamt, alarm)
    print(query)
    cursor = connection.cursor()
    cursor.execute(query)

    # 승하차 알람 등록시 마일리지 차감
    if alarm=='Y':
        query = "insert into megabus_mileage (mid, cretype, creamt, crewhere)" \
                "  values(%d, '사용', %d, '승하차알림')" % (int(mid), -50)
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

# 승차 대기 등록
def readyform (request):
    mid = request.session['mid']
    print("readyform mid:" + str(mid))

    # 버스노선 이용내역
    query = "select ulid, bnname, onbsname, offbsname, usedate from megabus_uselist " \
            "where mid=%d and status='R' order by usedate desc;" % int(mid)
    print(query)
    cursor = connection.cursor()
    row = cursor.execute(query)
    rst = row.fetchall()

    dic = {'mid': mid, 'rstlst': rst}

    return render(request, 'takeonoff/readyform.html', dic)

# 승차대기
def ready(request):
    mid = request.session['mid']
    print("ready mid:" + str(mid))

    useid = request.POST['ulid']

    # 버스노선 이용내역
    query = "select brid, bnname, onbsid, onord, offbsid, offord from megabus_uselist " \
            "where ulid=%d and status='R' order by usedate desc;" % int(useid)
    print(query)
    cursor = connection.cursor()
    row = cursor.execute(query)
    rst = row.fetchone()

    request.session['useid'] = useid
    request.session['brid'] = rst[0]
    request.session['bnname'] = rst[1]
    request.session['onbsid'] = rst[2]
    request.session['onord'] = rst[3]
    request.session['offbsid'] = rst[4]
    request.session['offord'] = rst[5]
    request.session['mstatus'] = "R"
    print(request.session['mstatus'])

    # 특정노선(예:1000번 버스노선)의 특정 정류장 도착 순서에 따른 차량id 추출 openAPI 연동 REST [XML]
    url = 'http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute'
    keystr = '?serviceKey=WS6IE%2F0nHkArdmPt3284YdVVLGtZPSuSQ0ANuFo463Hj3KU9zb7RpSz5hJHWQpWw0sE0Vbz9V4f7zBSdO7%2FR1A%3D%3D'
    param1 = '&stId=%s&busRouteId=%s&ord=%s' % (
    request.session['onbsid'], request.session['brid'], request.session['onord'])

    print(url + keystr + param1)
    response = requests.get(url + keystr + param1)
    soup = BeautifulSoup(response.text, 'html.parser')

    # soup의 모든 node는 소문자
    vehid1 = soup.find('vehid1').text
    print(vehid1)
    vehid2 = soup.find('vehid2').text
    print(vehid2)

    # 승차버스 아이디 준비
    request.session['vehid'] = vehid1

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

    if int(mid) > 0:
        dic = {'mid': mid, 'mileage': mileage}

        return render(request, 'mypage/mypage.html', dic)
    else:

        return render(request, 'member/login.html')

def uselist(request):
    mid = request.session['mid']
    print("uselist mid:" + str(mid))

    if int(mid) > 0:
        # 버스노선 이용내역
        query = "select ulid, bnid, onbsname, offbsname, usedate, bookmark from megabus_uselist " \
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
    print("uselist mid:" + str(mid))

    if int(mid) > 0:
        # 결제 내역
        query = "select a.ulid, b.payname, a.payamt , a.usedate " \
                "from megabus_uselist a, megabus_paytype b where a.pid = b.pid and a.mid=%d and a.pid  notnull " \
                "order by usedate desc;" % int(mid)
        print(query)
        cursor = connection.cursor()
        row = cursor.execute(query)
        rst = row.fetchall()

        dic = {'mid': mid, 'rstlst': rst}

        return render(request, 'mypage/paylist.html', dic)
    else:

        return render(request, 'member/login.html')

def mileagelist(request):
    mid = request.session['mid']
    print("uselist mid:" + str(mid))

    if int(mid) > 0:
        # 마일리지 사용 내역
        query = "select cretype, creamt, credate, crewhere " \
                "from megabus_mileage " \
                "where mid=%d " \
                "order by credate desc;" % int(mid)

        print(query)
        cursor = connection.cursor()
        row = cursor.execute(query)
        rst = row.fetchall()

        dic = {'mid': mid, 'rstlst': rst}

        return render(request, 'mypage/mileagelist.html', dic)
    else:

        return render(request, 'member/login.html')

def bookmark(request):
    mid = request.session['mid']
    print("makeqr mid:" + str(mid))
    ulid = request.POST['ulid']
    print("bookmark ulid:" + ulid)
    yn = request.POST['yn']
    print("bookmark yn:" + yn)

    # bookmark 처리
    query = "update megabus_uselist set bookmark='%s' where ulid=%d ;" % (yn, int(ulid))
    print(query)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()

    return render(request, 'main.html')

# 승차 QR 코드 생성
def makeqr(request):
    mid = request.session['mid']
    print("makeqr mid:" + str(mid))

    # local용
    homeurl = "http://127.0.0.1:8000/megabus/bussys/bus_geton"
    # real용
    #homeurl = "http://makecoding.pythonanywhere.com/megabus/bussys/bus_geton"
    qr = "https://chart.googleapis.com/chart?cht=qr&chl=%s?mid=%s&chs=200x200" % (homeurl, mid)


    return render(request, 'qr/QRcode.html', {'qr': qr})

# 하차 태깅 처리 > 버스 앱 하차용qr에 고정 url로 세팅됨.
def bus_getoff(request):
    # 승차등록에서 설정된 이용id
    useid = request.session['useid']
    print("bus_getoff useid:" + useid)

    # 이용상태 탑승으로 변경
    query = "update megabus_uselist set status='OFF' where ulid=%d ;" % (int(useid))
    print(query)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()

    request.session['mstatus'] = "OFF"

    return render(request, 'member/login.html')


#버스 단말기 용
# 승차 태깅 처리 (차량 배정 /
def bus_geton(request):
    # 버스단말기 qr태킹에서 넘어온 사용자 id
    mid = request.GET['mid']
    print("bus_take mid:" + mid)

    # 승차등록에서 설정된 이용id
    useid = request.session['useid']
    print("bus_take useid:" + useid)

    # 현재 차량아이디를 등록함.
    bnid = request.session['vehid']

    # 이용상태 탑승으로 변경
    query = "update megabus_uselist set status='ON', bnid=%d where ulid=%d ;" % (int(bnid), int(useid))
    print(query)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()

    request.session['mstatus'] = "ON"

    return render(request, 'main.html')

# 차량용 QR 코드 생성
def bus_makeqr(request):
    bnid = request.session['vehid']

    # local용
    homeurl = "http://127.0.0.1:8000/megabus/bussys/bus_getoff"
    # real용
    # homeurl = "http://makecoding.pythonanywhere.com/megabus/bussys/bus_getoff"
    qr = "https://chart.googleapis.com/chart?cht=qr&chl=%s&chs=200x200" % (homeurl)

    return render(request, 'qr/QRcode.html', {'qr': qr})
