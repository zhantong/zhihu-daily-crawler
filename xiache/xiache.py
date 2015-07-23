"""
	利用知乎日报API爬取“瞎扯”栏目所有文章。
	大体为首先获取全部瞎扯URL的后缀（API循环），然后逐个访问，处理后保存为HTML格式。
	API采用JSON格式。
    HTML文件进一步处理，删除作者头像图片、下载所有链接图片，替换链接后，利用CSS可以制作成电子书。
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
q_img = queue.Queue()  # 下载图片队列
xiache_list = []  # JSON格式，其中包含瞎扯URL后缀
content_list = []  # JSON格式，包含每日瞎扯内容
content = '' #HTML格式，全部瞎扯内容
headers = {  # 模拟浏览器
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'
}
file_name = 'final.html'  # 最终生成的文件名，还包括图片文件夹名
section='2'
def get_section():
    url='http://news-at.zhihu.com/api/3/sections'
    opener = urllib.request.build_opener()
    get = urllib.request.Request(url=url, headers=headers, method='GET')
    con = opener.open(get).read().decode('utf-8')
    con_json = json.loads(con)
    for section in con_json['data']:
        print(section['id'],section['name'],section['description'])
def get_xiache_list(start_date='20150101',end_date='20150722'):  # 获取JSON格式全部瞎扯信息，保存为数组
    print('获取链接地址...')
    # 最先访问URL，只提供最近18天的瞎扯URL信息
    url = 'http://news-at.zhihu.com/api/4/section/'+section
    opener = urllib.request.build_opener()
    get = urllib.request.Request(url=url, headers=headers, method='GET')
    con = opener.open(get).read().decode('utf-8')
    con_json = json.loads(con)  # 使用json模块处理
    for item in con_json['stories']:
        if item['date']>=start_date and item['date']<=end_date:
            xiache_list.append(item)
    #xiache_list.extend(con_json['stories'])  # 需要的JSON信息
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
        for item in con_json['stories']:
            if item['date']>=start_date and item['date']<=end_date:
                xiache_list.append(item)
        #xiache_list.extend(con_json['stories'])  # 加入数组


def trans_header(date, title):  # 作为HTML及电子书分隔每天瞎扯的标题
    trans = date[0:4] + '年' + str(int(date[4:6])) + \
        '月' + str(int(date[6:8])) + '日' + '  ' + \
        title  # 如“2015年7月4日  瞎扯·如何正确吐槽”
    return trans


def multi_thread(num, target):  # 多线程模板
    threads = []
    for i in range(num):
        d = threading.Thread(target=target)
        threads.append(d)
    for d in threads:
        d.start()
    for d in threads:
        d.join()


def get_xiache_content():  # 获取瞎扯内容
    def getting():  # 便于实现多线程抓取内容
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
    header = {}  # 将所有的日期标题组合成为dict，便于后期插入匹配
    for item in xiache_list:
        header[item['id']] = trans_header(item['date'], item['title'])
        q.put(str(item['id']))  # 瞎扯URL后缀
    multi_thread(10, getting)
    print('全部内容获取完！')


def to_html():
    global content
    print('开始转换为HTML格式')
    # list中dict按'id'排序，逆序
    content_list.sort(key=lambda obj: obj.get('id'), reverse=True)
    for line_json in content_list:  # 对每天的瞎扯操作
        r = re.findall(
            '(<div class="question">.*?<div class="view-more">.*?</div>)', line_json['body'], re.S)  # 分离出question这个div，去除原始内容中无用信息
        content = content + '<div class="day">\n<h1>' + \
            header[line_json['id']] + '</h1>\n'  # 添加一层div，以及一个h1标题，输入日期标题
        for question in r:
            content = content + question + '\n</div>\n'
        content = content + '</div>\n'
#    with codecs.open('content.html', 'w', 'utf-8') as f:  # 写入到本地文件
#        f.write(content)
    print('格式转换成功，已写入到本地文件！')


def dl_img():  # 下载HTML中链接的图片到本地，便于电子书制作
    print('正在下载图片...（视网络情况可能需要一定时间）')

    def getting():  # 便于多进程处理
        opener = urllib.request.build_opener()
        while(not q_img.empty()):
            img_url = q_img.get()
            get = urllib.request.Request(
                url=img_url, headers=headers, method='GET')
            try:
                img_b = opener.open(get).read()
            except Exception as e:
                print(e)
                print('重新下载...')
                q_img.put(img_url)
                continue
            with open(file_name.split('.')[-2] + '_files/' + img_url.split('/')[-1], 'wb') as f:
                f.write(img_b)
    if not os.path.exists(file_name.split('.')[-2] + '_files'):
        os.mkdir(file_name.split('.')[-2] + '_files')
    multi_thread(20, getting)
    print('图片全部下载完成！')


def post_work():  # 包括去除作者头像图片，和替换HTML中图片链接，并生成下载图片队列
    global content
#    with codecs.open('content.html', 'r', 'utf-8') as f:
#        content = f.read()
    content = re.sub(r'<img class="avatar".*?>', '', content)
    r = re.findall(r'src="(.*?jpg)"', content)
    for url in r:
        q_img.put(url)
        content = content.replace(
            url, './' + file_name.split('.')[-2] + '_files/' + url.split('/')[-1])
    with codecs.open(file_name, 'w', 'utf-8') as f:  # 写入最终生成HTML文件到本地
        f.write(content)
    dl_img()
    print('已删除作者头像，并下载全部链接图片！')

if __name__ == '__main__':
    get_xiache_list()
    get_xiache_content()
    to_html()
    post_work()
#    get_section()
