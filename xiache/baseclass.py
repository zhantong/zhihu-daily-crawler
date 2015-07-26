import urllib.request
import json
import threading

headers = {  # 模拟浏览器
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'
}
class BaseClass():
    def __init__(self):
        self.opener = None
    def build_opener(self):
        self.opener = urllib.request.build_opener()
        return self.opener

    def get_html(self,url):
        if self.opener == None:
            self.build_opener()
        get = urllib.request.Request(url, headers=headers, method='GET')
        return self.opener.open(get).read().decode('utf-8')
    def json_load(self, content):
        return json.loads(content)

    def json_dump(self, content):
        return json.dumps(content, ensure_ascii=False, sort_keys=True)
    def multi_thread(self,num, target):  # 多线程模板
        threads = []
        for i in range(num):
            d = threading.Thread(target=target)
            threads.append(d)
        for d in threads:
            d.start()
        for d in threads:
            d.join()