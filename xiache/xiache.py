"""
	利用知乎日报API爬取“瞎扯”栏目所有文章。
	大体为首先获取全部瞎扯URL的后缀（API循环），然后逐个访问，并存储到本地文件。
	API采用JSON格式。
"""
import json
import queue
import urllib.request
import codecs
import re
import threading
import queue
import os
q = queue.Queue()  # URL后缀队列
q_img=queue.Queue()
xiache_list = []  # JSON格式，其中包含瞎扯URL后缀
headers = {  # 模拟浏览器
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'
}


def get_xiache_list():  # 获取JSON格式全部瞎扯信息，保存为数组
    # 最先访问URL，只提供最近18天的瞎扯URL信息
    url = 'http://news-at.zhihu.com/api/4/section/2'
    opener = urllib.request.build_opener()
    get = urllib.request.Request(url=url, headers=headers, method='GET')
    con = opener.open(get).read().decode('utf-8')
    con_json = json.loads(con)  # 使用json模块处理
    xiache_list.extend(con_json['stories'])  # 需要的JSON信息
    print(con_json['timestamp'])
    while 1:
        try:
            time = con_json['timestamp']  # 终止条件为不含有timestamp变量
        except Exception:
            print('done')
            break
        print(time)
        get = urllib.request.Request(
            url=url + '/before/' + str(time), headers=headers, method='GET')  # 获取历史瞎扯URL信息
        try:
            con = opener.open(get).read().decode('utf-8')
        except Exception as e:  # 其他错误
            print(e)
            break
        con_json = json.loads(con)
        xiache_list.extend(con_json['stories'])  # 加入数组


def trans_header(date, title):
    trans = date[0:4] + '年' + str(int(date[4:6])) + \
        '月' + str(int(date[6:8])) + '日' + '  ' + title
    return trans

content_list = []


def get_xiache_content():  # 获取瞎扯内容
    def getting():
        url = 'http://news-at.zhihu.com/api/4/story/'  # 此URL与瞎扯URL后缀拼接
        opener = urllib.request.build_opener()
        while not q.empty():
            xiache_id = q.get()
            get = urllib.request.Request(
                url=url + xiache_id, headers=headers, method='GET')
            con = opener.open(get).read().decode('utf-8')
            content_list.append(json.loads(con))
            print(xiache_id, 'done')
    global header
    header = {}
    for item in xiache_list:
        header[item['id']] = trans_header(item['date'], item['title'])
        q.put(str(item['id']))  # 瞎扯URL后缀
    threads = []
    for i in range(10):  # 这个查询API如果访问过于频繁会封IP，但这里还是保留了多线程功能，应对可能出现的情况
        d = threading.Thread(target=getting)
        threads.append(d)
    for d in threads:
        d.start()
    for d in threads:
        d.join()
    print('write content done')


def to_html():
    content=''
    content_list.sort(key=lambda obj:obj.get('id'),reverse=True)
    for line_json in content_list:
        #line_json = json.loads(line)
        r = re.findall(
            '(<div class="question">.*?<div class="view-more">.*?</div>)', line_json['body'], re.S)
        content = content + '<div class="day">\n<h1>' + \
            header[line_json['id']] + '</h1>\n'
        for question in r:
            content = content + question + '\n</div>\n'
        content = content + '</div>\n'
    with codecs.open('conten.html', 'w', 'utf-8') as f:
        f.write(content)
    print('all done')
def dl_img():
    print('downloading images')
    def getting():
        opener = urllib.request.build_opener()
        while(not q_img.empty()):
            img_url=q_img.get()
            get=urllib.request.Request(url=img_url,headers=headers,method='GET')
            img_b=opener.open(get).read()
            with open('dl_files/'+img_url.split('/')[-1],'wb') as f:
                f.write(img_b)
    if not os.path.exists('dl_files'):
        os.mkdir('dl_files')
    threads=[]
    for i in range(10):  # 这个查询API如果访问过于频繁会封IP，但这里还是保留了多线程功能，应对可能出现的情况
        d = threading.Thread(target=getting)
        threads.append(d)
    for d in threads:
        d.start()
    for d in threads:
        d.join()
    print('download images finished')
def post_work():
    with codecs.open('conten.html','r','utf-8') as f:
        content=f.read()
    content=re.sub(r'<img class="avatar".*?>','',content)
    r=re.findall(r'src="(.*?jpg)"',content)
    for url in r:
        q_img.put(url)
        content=content.replace(url,'./dl_files/'+url.split('/')[-1])
    with codecs.open('dl.html','w','utf-8') as f:
        f.write(content)
    dl_img()
    print('postwork done')

if __name__ == '__main__':
    get_xiache_list()
    get_xiache_content()
    to_html()
    post_work()
