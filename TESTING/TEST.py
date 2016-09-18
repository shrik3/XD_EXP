import urllib.request
import urllib.parse
import urllib.error
from bs4 import BeautifulSoup
import re

pattern = re.compile(r'"__VIEWSTATE".*value="(.*)"')
pattern2 = re.compile(r'name="__VIEWSTATEGENERATOR".*value="(.*)"')

req = urllib.request.Request("http://wlsy.xidian.edu.cn/phyEws/default.aspx")
res = urllib.request.urlopen(req)

page = res.read().decode("GBK")
raw = BeautifulSoup(page)

res = pattern.findall(page)[0]
res2 = pattern2.findall(page)[0]
print(res)
print(res2)