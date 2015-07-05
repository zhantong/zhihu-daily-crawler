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
file_name='final.html'

def get_xiache_list():  # 获取JSON格式全部瞎扯信息，保存为数组
    print('获取链接地址...')
    # 最先访问URL，只提供最近18天的瞎扯URL信息
    url = 'http://news-at.zhihu.com/api/4/section/2'
    opener = urllib.request.build_opener()
    get = urllib.request.Request(url=url, headers=headers, method='GET')
    con = opener.open(get).read().decode('utf-8')
    con_json = json.loads(con)  # 使用json模块处理
    xiache_list.extend(con_json['stories'])  # 需要的JSON信息
    while 1:
        try:
            time = con_json['timestamp']  # 终止条件为不含有timestamp变量
        except Exception:
            print('全部链接地址获取完！')
            break
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

def multi_thread(num,target):
    threads = []
    for i in range(num):  
        d = threading.Thread(target=target)
        threads.append(d)
    for d in threads:
        d.start()
    for d in threads:
        d.join()
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
    print('获取内容...（视网络情况可能需要一定时间）')
    global header
    header = {}
    for item in xiache_list:
        header[item['id']] = trans_header(item['date'], item['title'])
        q.put(str(item['id']))  # 瞎扯URL后缀
    multi_thread(10,getting)
    print('全部内容获取完！')


def to_html():
    print('开始转换为HTML格式')
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
    print('格式转换成功，已写入到本地文件！')
def dl_img():
    print('正在下载图片...（视网络情况可能需要一定时间）')
    def getting():
        opener = urllib.request.build_opener()
        while(not q_img.empty()):
            img_url=q_img.get()
            get=urllib.request.Request(url=img_url,headers=headers,method='GET')
            img_b=opener.open(get).read()
            with open(file_name.split('.')[-2]+'_files/'+img_url.split('/')[-1],'wb') as f:
                f.write(img_b)
    if not os.path.exists(file_name.split('.')[-2]+'_files'):
        os.mkdir(file_name.split('.')[-2]+'_files')
    multi_thread(20,getting)
    print('图片全部下载完成！')
def post_work():
    with codecs.open('conten.html','r','utf-8') as f:
        content=f.read()
    content=re.sub(r'<img class="avatar".*?>','',content)
    r=re.findall(r'src="(.*?jpg)"',content)
    for url in r:
        q_img.put(url)
        content=content.replace(url,'./'+file_name.split('.')[-2]+'_files/'+url.split('/')[-1])
    with codecs.open(file_name,'w','utf-8') as f:
        f.write(content)
    dl_img()
    print('已删除作者头像，并下载全部链接图片！')

if __name__ == '__main__':
    get_xiache_list()
    get_xiache_content()
    to_html()
    post_work()
