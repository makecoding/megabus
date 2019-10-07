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
        mid = request.GET['mid']

        query = "select status from megabus_member where mid=%d;" % int(mid)
        cursor = connection.cursor()
        row = cursor.execute(query)
        status = row.fetchone()

        print("status : "+status[0])
        # 탑승대기 상태라면 승차 알림를 위한 데이터 전달
        if status[0] == 'R':
            query = "select ulid, bnid, onbsid, brid, onord  from megabus_uselist " \
                    "where mid=%d and status='R';" % int(mid)
            print(query)
            cursor = connection.cursor()
            row = cursor.execute(query)
            rst = row.fetchone()
            print("rst : " + str(rst))
            info = [status[0], rst]

            # info = str(status[0])+","+str(rst[0])+","+str(rst[1])+","+str(rst[2])+","+str(rst[3])
            print(info)
            return Response(info)
        # 탑승 중이라면 하차 알림을 위한 데이터 전달
        elif status[0] == 'ON':
            query = "select ulid, bnid, offbsid, brid, offord  from megabus_uselist " \
                    "where mid=%d and status='ON';" % int(mid)
            print(query)
            cursor = connection.cursor()
            row = cursor.execute(query)
            rst = row.fetchone()
            print("rst : " + str(rst))
            info = [status[0], rst]

            # info = str(status[0])+","+str(rst[0])+","+str(rst[1])+","+str(rst[2])+","+str(rst[3])
            print(info)
            return Response(info)
        else:
            return Response([status[0], []])

class GetBusid(APIView):
    def get (self, request, format=None):
        return Response(request.session['vehid'])

# 승차 버스 알림
class ReadyOn(APIView):
    def get(self, request, format=None):
        bnid = request.GET['bnid']
        onbsid = request.GET['onbsid']
        brid = request.GET['brid']
        onord = request.GET['onord']

        # 특정노선(예:1000번 버스노선)의 하차 정류장 도착 순서에 따른 차량id 추출 openAPI 연동 REST [XML]
        url = 'http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute'
        keystr = '?serviceKey=WS6IE%2F0nHkArdmPt3284YdVVLGtZPSuSQ0ANuFo463Hj3KU9zb7RpSz5hJHWQpWw0sE0Vbz9V4f7zBSdO7%2FR1A%3D%3D'
        param1 = '&stId=%s&busRouteId=%s&ord=%s' % (onbsid, brid, onord)

        print(url + keystr + param1)
        response = requests.get(url + keystr + param1)
        soup = BeautifulSoup(response.text, 'html.parser')

        # soup의 모든 node는 소문자
        vehid1 = soup.find('vehid1').text
        print(vehid1)
        vehid2 = soup.find('vehid2').text
        print(vehid2)
        
        rst = "N"
        # 승차정류장 접근 버스가 현재 등록한 버스와 동일한 경우
        if bnid == vehid1:
            rst = "Y"

        return Response(rst)

# 공통 알림페이지
def notice(request):

    return render(request, 'notipage.html', {'msg':'하하하하하'})

# 모바일앱 사용자 세션 등록
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
    query = "select ulid, bnname, onbsname, offbsname from megabus_uselist " \
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
    if int(mid)>0:
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
            "where mid=%d and status='N' order by usedate desc;" % int(mid)
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
            "where ulid=%d order by usedate desc;" % int(useid)
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

    #테스트용
    print(vehid2+":"+str(request.session['onbsid'])+":"+str(request.session['brid'])+":"+str(request.session['onord']))

    # 승차버스 아이디 준비
    if (int(vehid2)>0):
        request.session['vehid'] = vehid2

    # 이용건의 이용상태 승차대기 및 탑승 예정버스 아이디  변경
    query = "update megabus_uselist set status='R', bnid=%d where ulid=%d ;" % (int(vehid2), int(useid))
    print(query)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()


    # 사용자의 이용상태 승차대기 으로 변경
    query = "update megabus_member set status='R' where mid=%d ;" % (int(mid))
    print(query)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()

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
    # 사용자가 스캔한 url로 넘어옴.
    mid = request.GET['mid']
    print("bus_take mid:" + mid)

    query = "select ulid from megabus_uselist " \
            "where status='ON' and mid=%d;" % int(mid)
    print(query)
    cursor = connection.cursor()
    row = cursor.execute(query)
    rst = row.fetchone()

    # 이용내역 이용상태 탑승으로 변경
    query = "update megabus_uselist set status='OFF' where ulid=%d ;" % (rst[0])
    print(query)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()

    # 사용자의 이용상태 승차대기 으로 변경
    query = "update megabus_member set status='OFF' where mid=%d ;" % (int(mid))
    print(query)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()

    #request.session['mstatus'] = "OFF"

    return render(request, 'main.html')


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
    #bnid = request.session['vehid']
    # session 무시됨. 사용자 리스트에 등록된 예정버스를 사용함.
    query = "select bnid from megabus_uselist " \
            "where status='R' and mid=%d;" % int(mid)
    print(query)
    cursor = connection.cursor()
    row = cursor.execute(query)
    rst = row.fetchone()
    bnid = rst[0]

    # 이용상태 탑승으로 변경
    query = "update megabus_uselist set status='ON', bnid=%d where ulid=%d ;" % (int(bnid), int(useid))
    print(query)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()

    # 사용자의 이용상태 승차대기 으로 변경
    query = "update megabus_member set status='ON' where mid=%d ;" % (int(mid))
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
    homeurl = "http://127.0.0.1:8000/megabus/getoff/bus_getoff"
    # real용
    # homeurl = "http://makecoding.pythonanywhere.com/megabus/getoff/bus_getoff"
    qr = "https://chart.googleapis.com/chart?cht=qr&chl=%s&chs=200x200" % (homeurl)

    return render(request, 'qr/QRcode.html', {'qr': qr})
