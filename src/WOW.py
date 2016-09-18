import urllib.request
import urllib.parse
import urllib
import urllib.error
import re
import threading

headers = {}
data = {
    "func":"login-session",
    "login_source":"bor-info",
    "bor_id":"",
    "bor_verification":"",
    "bor_library":"XDU50"

}


class GET():
    def __init__(self,data,UID):
        self.data = data
        self.UID = UID
        self.url = 'http://al.lib.xidian.edu.cn/F/?func=file&file_name=login-session'


    def PrepareData(self,UID):
        data = self.data
        data['bor_id'] = UID
        data['bor_verification'] = '123456'

    def Login(self,data):
        post_data = urllib.parse.urlencode(data)
        bin_data = post_data.encode('utf-8')
        try:
            request = urllib.request.Request(self.url,data=data,headers=headers)
            response= urllib.request.urlopen(request)
            html = response.read()
            return html
        except urllib.error as e:
            print(e.code)
            return None



    def Control(self):






