import random
import time
import urllib
import http.cookiejar
import json

# 伪造请求头
headerNum = random.randint(0, 3)
fake_headers = [{'Host': 'newxk.urp.seu.edu.cn',
                 'Proxy-Connection': 'keep-alive',
                 'Origin': 'http://newxk.urp.seu.edu.cn',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1'},
                {'Host': 'newxk.urp.seu.edu.cn',
                 'Origin': 'http://newxk.urp.seu.edu.cn',
                 'Connection': 'keep-alive',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'},
                {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                 'Connection': 'keep-alive',
                 'Host': 'newxk.urp.seu.edu.cn',
                 'Origin': 'http://newxk.urp.seu.edu.cn',
                 'User-Agent': 'Mozilla/6.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0'},
                {'Host': 'newxk.urp.seu.edu.cn',
                 'Connection': 'keep-alive',
                 'Accept': 'text/html, */*; q=0.01',
                 'User-Agent': 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
                 'Origin': 'http://newxk.urp.seu.edu.cn'}]


def login(username, password, vercode, vtoken, nBatch):
    """
    登录模块
    参数列表：用户名 密码 验证码 验证码token 批次码
    """
    # print 'header is ' + str(headerNum)
    header = fake_headers[headerNum]
    header.setdefault('Referer', 'http://newxk.urp.seu.edu.cn/')
    url = "http://newxk.urp.seu.edu.cn/xsxkapp/sys/xsxkapp/student/check/login.do?"
    qsData = {
        "timestamp": str(int(time.time())),
        "loginName": str(username),
        "loginPwd": str(password),
        "verifyCode": vercode,
        "vtoken": vtoken
    }
    query_string = urllib.parse.urlencode(qsData)
    url += query_string
    req = urllib.request.Request(url, headers=header)
    cookie = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookie))
    urllib.request.install_opener(opener)
    response = opener.open(req)
    content = response.read().decode('utf-8')
    jsonObject = json.loads(content)
    if jsonObject['msg'] == '验证码不正确':
        input('验证码不正确,程序退出')
        exit(-1)
    Logintoken = jsonObject['data']['token']
    Msg = jsonObject['msg']
    print(Logintoken)
    print(Msg)
    # 如果登录成功，获取选课批次代码
    url = "http://newxk.urp.seu.edu.cn/xsxkapp/sys/xsxkapp/elective/batch.do?timestrap=" + \
        str(int(time.time()))
    data = urllib.request.urlopen(url)
    content = data.read().decode("utf-8")
    electiveBatchCode = json.loads(
        content)['dataList'][int(nBatch)]['code']
    print("批次码:" + electiveBatchCode)
    return Logintoken, electiveBatchCode


def get_verifycode():
    """
    获取验证码
    """
    # 获取当前时间戳
    timestamp = time.time()
    url = 'http://newxk.urp.seu.edu.cn/xsxkapp/sys/xsxkapp/student/4/vcode.do?timestamp=' + \
        str(int(timestamp))
    # global vtoken
    # 创建cooliejar对象
    cookie = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookie))
    urllib.request.install_opener(opener)
    req = urllib.request.Request(url)
    file = opener.open(req)
    # 获取验证码vtoken
    vtoken = json.load(file)['data']['token']
    print(vtoken)
    # 获取验证码
    img = urllib.request.urlopen(
        'http://newxk.urp.seu.edu.cn/xsxkapp/sys/xsxkapp/student/vcode/image.do?vtoken=' + vtoken, timeout=20)
    f = open('verifycode.jpg', 'wb')
    f.write(img.read())
    f.close()
    return vtoken


def getCourse(Logintoken, username, electiveBatchCode, url, teachingClassType):
    """
    获取课程列表
    """
    header = fake_headers[headerNum]
    header.setdefault(
        'Referer', 'http://newxk.urp.seu.edu.cn/xsxkapp/sys/xsxkapp/*default/grablessons.do?token='+str(Logintoken))
    header.setdefault('token', Logintoken)
    jsonData = {
        "data": {
            "studentCode": username,
            "campus": "1",
            "electiveBatchCode": electiveBatchCode,
            "isMajor": "1",
            "teachingClassType": teachingClassType,
            "checkConflict": "2",
            "checkCapacity": "2",
            "queryContent": ""
        },
        "pageSize": str(100+random.randint(10, 50)),
        "pageNumber": "0",
        "order": ""
    }
    postdata = urllib.parse.urlencode(
        {"querySetting": json.dumps(jsonData)}).encode('utf-8')
    req = urllib.request.Request(url, postdata, headers=header)
    response = urllib.request.urlopen(req, timeout=20)
    content = response.read().decode('utf-8')
    return content
    # JsonParse(list_recommend, content)
    pass


def CourseJsonParse(datalist, StrJson):
    """
    课表Json数据的解析
    """
    print("正在进行课表Json数据的解析")
    # 清空现有记录
    del datalist[:]
    #datalist = []
    jsonObject = json.loads(StrJson)
    totalCount = jsonObject['totalCount']
    if jsonObject['msg'] == '查询结果:该学生不能在批次中选课':
        print(jsonObject['msg'], "请检查批次码")
        exit(0)
    for i in range(0, int(totalCount)):
        str_select = str(jsonObject['dataList'][i]['selected'])
        if str_select:
            for j in range(0, int(jsonObject['dataList'][i]['number'])):
                classData = dict(
                    courseName=jsonObject['dataList'][i]['courseName'])
                classData['isFull'] = str(
                    jsonObject['dataList'][i]['tcList'][j]['isFull'])
                classData['isConflict'] = str(
                    jsonObject['dataList'][i]['tcList'][j]['isConflict'])
                classData['teachingClassID'] = str(
                    jsonObject['dataList'][i]['tcList'][j]['teachingClassID'])
                classData['isChoose'] = str(
                    jsonObject['dataList'][i]['tcList'][j]['isChoose'])
                classData['teacherName'] = str(
                    jsonObject['dataList'][i]['tcList'][j]['teacherName'])
                classData['teachingPlace'] = str(
                    jsonObject['dataList'][i]['tcList'][j]['teachingPlace'])
                datalist.append(classData)
    # print(datalist)
    print("json解析完毕")


def dropclass(Logintoken, username, electiveBatchCode, teachingClassId):
    """
    发送退课请求
    """
    # 获取当前时间戳
    timestamp = time.time()
    print("正在发送退选请求")
    header = fake_headers[headerNum]
    header.setdefault('Referer',
                      'http://newxk.urp.seu.edu.cn/xsxkapp/sys/xsxkapp/*default/grablessons.do?token=' + str(
                          Logintoken))
    header.setdefault('token', Logintoken)
    url = 'http://newxk.urp.seu.edu.cn/xsxkapp/sys/xsxkapp/elective/deleteVolunteer.do?'
    qsData = {
        "timestamp": str(int(timestamp)),
        "deleteParam": {
            "data": {
                "operationType": "2",
                "studentCode": username,
                "electiveBatchCode": electiveBatchCode,
                "teachingClassId": teachingClassId,
                "isMajor": "1"
            }
        }
    }
    query_string = urllib.parse.urlencode(qsData)
    url += query_string
    url = url.replace("+", "")
    url = url.replace("%27", "%22")
    req = urllib.request.Request(url, headers=header)
    response = urllib.request.urlopen(req, timeout=20)
    content = response.read().decode('utf-8')
    # print("选课完成，选课返回结果:"+content)
    jsonObject = json.loads(content)
    msg = jsonObject['msg']
    print(msg)
    return msg
    pass


def pickclass(Logintoken, username, electiveBatchCode, teachingClassId, teachingClassType):
    """
    自动发送选课请求
    """
    print("正在发送选课请求")
    header = fake_headers[headerNum]
    header.setdefault('Referer',
                      'http://newxk.urp.seu.edu.cn/xsxkapp/sys/xsxkapp/*default/grablessons.do?token=' + str(
                          Logintoken))
    header.setdefault('token', Logintoken)
    url = 'http://newxk.urp.seu.edu.cn/xsxkapp/sys/xsxkapp/elective/volunteer.do'
    jsonData = {
        "data": {
            "operationType": "1",
            "studentCode": username,
            "electiveBatchCode": electiveBatchCode,
            "teachingClassId": teachingClassId,
            "isMajor": "1",
            "campus": "1",
            "teachingClassType": teachingClassType,
        }
    }

    postdata = urllib.parse.urlencode({
        "addParam": json.dumps(jsonData)
    }).encode('utf-8')
    req = urllib.request.Request(url, postdata, headers=header)
    ctrl_val = 1
    while ctrl_val:
        ctrl_val = 0
        try:
            response = urllib.request.urlopen(req, timeout=20)
        except Exception as e:
            ctrl_val = 1
            print("timeout, try again")
            time.sleep(1)
    content = response.read().decode('utf-8')
    jsonObject = json.loads(content)
    msg = jsonObject['msg']
    print(msg)
    return msg


def JsonParse(StrJson):
    '''
    解析课表Json数据
    '''
    print("正在进行课表Json数据的解析")
    datalist = []
    jsonObject = json.loads(StrJson)
    totalCount = jsonObject['totalCount']
    if totalCount == None:
        totalCount = 0
    if jsonObject['msg'] == '查询结果:该学生不能在批次中选课':
        print(jsonObject['msg'], "请检查批次码")
        exit(0)
    for i in range(0, int(totalCount)):
        str_select = str(jsonObject['dataList'][i]['selected'])
        if str_select:  # 未排除已选的课
            for j in range(0, int(jsonObject['dataList'][i]['number'])):
                classData = dict(
                    courseName=jsonObject['dataList'][i]['courseName'])
                classData['isFull'] = str(
                    jsonObject['dataList'][i]['tcList'][j]['isFull'])
                classData['isConflict'] = str(
                    jsonObject['dataList'][i]['tcList'][j]['isConflict'])
                classData['teachingClassID'] = str(
                    jsonObject['dataList'][i]['tcList'][j]['teachingClassID'])
                classData['isChoose'] = str(
                    jsonObject['dataList'][i]['tcList'][j]['isChoose'])
                classData['teacherName'] = str(
                    jsonObject['dataList'][i]['tcList'][j]['teacherName'])
                classData['teachingPlace'] = str(
                    jsonObject['dataList'][i]['tcList'][j]['teachingPlace'])
                datalist.append(classData)
    # print(datalist)
    print("json解析完毕")
    return datalist
