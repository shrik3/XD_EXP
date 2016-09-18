import re
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar
import urllib
import threading

uid =
pwd = 

class Exp():
    __slots__ = ('week', 'time', 'type', 'name', 'tag')


class EXP_PARSER():
    def __init__(self, uid, pwd):
        self.exurl = "http://wlsy.xidian.edu.cn/phyEws/student/addexpe.aspx"
        self.uid = uid
        self.pwd = pwd

    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               "Accept-Encoding": "gzip, deflate,sdch",
               "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2",
               "Connection": "keep-alive",
               "Host": "wlsy.xidian.edu.cn",
               "Referer": "http://wlsy.xidian.edu.cn/phyEws/student.aspx",
               "Upgrade-Insecure-Requests": "1",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36"}

    def GetListPage(self):

        launcher = Launcher(self.uid, str(self.pwd))
        page = launcher.Login_And_Get_Page()
        try:
            req = urllib.request.Request(self.exurl, headers=self.headers)
            res = urllib.request.urlopen(req)
            page = res.read().decode("GBK")
            return page
        except urllib.error as e:
            print(e.code)

    def GetExpPostArgs(self, page):
        patterns = Launcher.patterns
        data = {}
        for i in patterns.keys():
            data[str(i)] = str(patterns[i].findall(page)[0])
        data["__EVENTARGUMENT"] = ''
        data["__LASTFOCUS"] = ''
        data["t1"] = ''
        return data

    def TraverseAll(self):
        week_pattern = re.compile(r'option value="(\d*)"')
        time_pattern = re.compile(r'option value="(\d\D)"')
        type_pattern = re.compile(r'value="(\d*)">物理实验')
        name_pattern = re.compile(r'option value="(\D\d\d)"')
        tag_pattern = re.compile(r'option value="\D\d\d">(.*)</option>')
        view_state_pattern = re.compile(r'"__VIEWSTATE".*value="(.*)"')
        event_validation_pattern = re.compile(r'id="__EVENTVALIDATION" value="(.*)"')

        weeklist = []
        timelist = []

        available_exp = []

        init_page = self.GetListPage()
        expe_type = re.findall(type_pattern, init_page)[0]
        # 拉取可选周次列表
        weeklist = re.findall(week_pattern, init_page)
        raw_data = self.GetExpPostArgs(init_page)
        cur_data = raw_data

        cur_data["ExpeClassList"] = expe_type
        cur_data["__VIEWSTATE"] = view_state_pattern.findall(init_page)[0]
        cur_data["__EVENTVALIDATION"] = event_validation_pattern.findall(init_page)[0]
        # print(cur_data)

        # 遍历所有可选周次,获取所有可选的实验时间
        for i in weeklist:

            cur_data["__EVENTTARGET"] = 'ExpeWeekList'
            cur_data["ExpeWeekList"] = str(i)
            data_to_post = urllib.parse.urlencode(cur_data).encode("utf-8")
            req = urllib.request.Request(self.exurl, headers=self.headers, data=data_to_post)
            res = urllib.request.urlopen(req)
            page = res.read().decode("GBK")
            # 更新 form data
            cur_data["__VIEWSTATE"] = view_state_pattern.findall(page)[0]
            cur_data["__EVENTVALIDATION"] = event_validation_pattern.findall(page)[0]
            cur_timelist = time_pattern.findall(page)
            for j in cur_timelist:
                timelist.append(i + j)

        # 遍历可选时段,拉取对应试验名称及代号
        cur_data["__EVENTTARGET"] = 'ExpeTimeList'
        for i in timelist:
            time = i[2:4]
            week = i[:-2]
            cur_data["ExpeWeekList"] = week
            cur_data["ExpeTimeList"] = time
            data_to_post = urllib.parse.urlencode(cur_data).encode("utf-8")
            req = urllib.request.Request(self.exurl, headers=self.headers, data=data_to_post)
            res = urllib.request.urlopen(req)
            page = res.read().decode("GBK")
            namelist = name_pattern.findall(page)
            taglist = tag_pattern.findall(page)

            # 更新form data
            cur_data["__EVENTVALIDATION"] = event_validation_pattern.findall(page)[0]
            cur_data["__VIEWSTATE"] = view_state_pattern.findall(page)[0]

            if namelist:
                for j in namelist:
                    cur_exp = Exp()
                    cur_exp.name = j
                    cur_exp.tag = taglist[0]
                    taglist.pop(0)
                    cur_exp.type = expe_type
                    cur_exp.time = time
                    cur_exp.week = week
                    available_exp.append(cur_exp)

        return available_exp


class Launcher():
    def __init__(self, uid, pwd):
        self.uid = uid
        self.pwd = pwd
        self.url = "http://wlsy.xidian.edu.cn/phyEws/default.aspx"

    patterns = {}
    patterns["__VIEWSTATE"] = re.compile(r'"__VIEWSTATE".*value="(.*)"')
    patterns["__VIEWSTATEGENERATOR"] = re.compile(r'name="__VIEWSTATEGENERATOR".*value="(.*)"')
    patterns["__EVENTVALIDATION"] = re.compile(r'id="__EVENTVALIDATION" value="(.*)"')

    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2",
               "Cache-Control": "max-age=0",
               "Connection": "keep-alive",
               "Content-Length": "443",
               "Content-Type": "application/x-www-form-urlencoded",
               "Host": "wlsy.xidian.edu.cn",
               "Origin": "http://wlsy.xidian.edu.cn",
               "Referer": "http://wlsy.xidian.edu.cn/phyEws/default.aspx",
               "Upgrade-Insecure-Requests": "1",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36"}

    def GetLoginArgs(self, page):
        data = {}
        patterns = self.patterns
        for i in patterns.keys():
            data[str(i)] = str(self.patterns[i].findall(page)[0])
        data["__EVENTTARGET"] = ''
        data["__EVENTARGUMENT"] = ''
        data["login1$UserRole"] = 'Student'
        data["login1$btnLogin.x"] = '27'
        data["login1$btnLogin.y"] = '6'
        return data

    def GetPage(self, url):
        try:
            req = urllib.request.Request(url)
            res = urllib.request.urlopen(req)
            page = res.read().decode("GBK")
            return page
        except urllib.error as e:
            print(e.code)

    def enableCookies(self):
        cookie_container = http.cookiejar.CookieJar()
        cookie_support = urllib.request.HTTPCookieProcessor(cookie_container)
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
        urllib.request.install_opener(opener)

    def Login_And_Get_Page(self):
        url = 'http://wlsy.xidian.edu.cn/phyEws/default.aspx'
        self.enableCookies()
        page = self.GetPage(url)
        data = self.GetLoginArgs(page)
        data['login1$StuLoginID'] = str(self.uid)
        data['login1$StuPassword'] = str(self.pwd)
        data_to_post = urllib.parse.urlencode(data).encode("utf-8")
        try:
            req = urllib.request.Request(url, headers=self.headers, data=data_to_post)
            res = urllib.request.urlopen(req)
            page = res.read().decode("GBK")
            return page
        except:
            pass


class Fuck():
    def __init__(self,exps):
        self.exps = exps

    view_state_pattern = re.compile(r'"__VIEWSTATE".*value="(.*)"')
    exurl = "http://wlsy.xidian.edu.cn/phyEws/student/addexpe.aspx"
    event_validation_pattern = re.compile(r'id="__EVENTVALIDATION" value="(.*)"')
    init_page = EXP_PARSER.GetListPage()
    type_pattern = re.compile(r'value="(\d*)">物理实验')
    expe_type = re.findall(type_pattern, init_page)[0]


    raw_data = self.GetExpPostArgs(init_page)
    cur_data = raw_data


    cur_data["__VIEWSTATE"] = view_state_pattern.findall(init_page)[0]
    cur_data["__EVENTVALIDATION"] = event_validation_pattern.findall(init_page)[0]
    cur_data["ExpeClassList"] = expe_type
    # print(cur_data)

    # 遍历所有可选周次,获取所有可选的实验时间
    for i in exps:

        cur_data["__EVENTTARGET"] = 'ExpeWeekList'
        cur_data["ExpeWeekList"] = i.week
        data_to_post = urllib.parse.urlencode(cur_data).encode("utf-8")
        req = urllib.request.Request(self.exurl, headers=EXP_PARSER.headers, data=data_to_post)
        res = urllib.request.urlopen(req)
        page = res.read().decode("GBK")
        # 更新 form data
        cur_data["__VIEWSTATE"] = view_state_pattern.findall(page)[0]
        cur_data["__EVENTVALIDATION"] = event_validation_pattern.findall(page)[0]

        cur_data["__EVENTTARGET"] = 'ExpeTimeList'
        cur_data["ExpeTimeList"] = i.time
        data_to_post = urllib.parse.urlencode(cur_data).encode("utf-8")
        req = urllib.request.Request(exurl, headers=EXP_PARSER.headers, data=data_to_post)
        res = urllib.request.urlopen(req)
        page = res.read().decode("GBK")
        # 更新 form data
        cur_data["__VIEWSTATE"] = view_state_pattern.findall(page)[0]
        cur_data["__EVENTVALIDATION"] = event_validation_pattern.findall(page)[0]

        cur_data["__EVENTTARGET"] = 'ExpeNameList'
        cur_data["ExpeNameList"] = i.name
        data_to_post = urllib.parse.urlencode(cur_data).encode("utf-8")
        req = urllib.request.Request(exurl, headers=EXP_PARSER.headers, data=data_to_post)
        res = urllib.request.urlopen(req)
        page = res.read().decode("GBK")
        # 更新 form data
        cur_data["__VIEWSTATE"] = view_state_pattern.findall(page)[0]
        cur_data["__EVENTVALIDATION"] = event_validation_pattern.findall(page)[0]

        cur_data["btnAdd.x"] = '24'
        cur_data["btnAdd.y"] = '11'
        data_to_post = urllib.parse.urlencode(cur_data).encode("utf-8")
        req = urllib.request.Request(exurl, headers=EXP_PARSER.headers, data=data_to_post)
        res = urllib.request.urlopen(req)
        page = res.read().decode("GBK")
