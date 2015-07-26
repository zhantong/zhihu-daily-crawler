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
import os
import baseclass
headers = {  # 模拟浏览器
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'
}

file_name = 'final.html'  # 最终生成的文件名，还包括图片文件夹名
section='2'
class Zhihu(baseclass.BaseClass):
    def __init__(self):
        self.info_list=[]
        self.titles={}
        self.id_queue=queue.Queue()
        self.content_list=[]
        self.content=''
        self.img_url_queue=queue.Queue()
        baseclass.BaseClass.__init__(self)
    def get_section(self):
        url='http://news-at.zhihu.com/api/3/sections'
        con=self.get_html(url)
        con_json = json.loads(con)
        for section in con_json['data']:
            print(section['id'],section['name'],section['description'])
    def get_list(self,start_date='20150701',end_date='20150722'):  # 获取JSON格式全部瞎扯信息，保存为数组
        print('获取链接地址...')
        # 最先访问URL，只提供最近18天的瞎扯URL信息
        url = 'http://news-at.zhihu.com/api/4/section/'+section
        con=self.get_html(url)
        con_json = self.json_load(con)  # 使用json模块处理
        for item in con_json['stories']:
            if item['date']>=start_date and item['date']<=end_date:
               self.titles[item['id']]=self.trans_header(item['date'], item['title'])
               self.id_queue.put(str(item['id']))
        #xiache_list.extend(con_json['stories'])  # 需要的JSON信息
        while 1:
            try:
                time = con_json['timestamp']  # 终止条件为不含有timestamp变量
            except Exception:
                print('全部链接地址获取完！')
                break
            try:
                con=self.get_html(url + '/before/' + str(time))
            except Exception as e:  # 其他错误
                print(e)
                break
            con_json = self.json_load(con)
            for item in con_json['stories']:
                if item['date']>=start_date and item['date']<=end_date:
                   self.titles[item['id']]=self.trans_header(item['date'], item['title'])
                   self.id_queue.put(str(item['id']))
            #xiache_list.extend(con_json['stories'])  # 加入数组


    def trans_header(self,date, title):  # 作为HTML及电子书分隔每天瞎扯的标题
        trans = date[0:4] + '年' + str(int(date[4:6])) + \
            '月' + str(int(date[6:8])) + '日' + '  ' + \
            title  # 如“2015年7月4日  瞎扯·如何正确吐槽”
        return trans




    def get_content(self):  # 获取瞎扯内容
        def dl():  # 便于实现多线程抓取内容
            url = 'http://news-at.zhihu.com/api/4/story/'  # 此URL与瞎扯URL后缀拼接
            opener = urllib.request.build_opener()
            while not self.id_queue.empty():
                xiache_id = self.id_queue.get()
                get = urllib.request.Request(
                    url=url + xiache_id, headers=headers, method='GET')
                con = opener.open(get).read().decode('utf-8')
                self.content_list.append(json.loads(con))
        print('获取内容...（视网络情况可能需要一定时间）')
        self.multi_thread(10, dl)
        print('全部内容获取完！')


    def to_html(self):
        print('开始转换为HTML格式')
        r_question=re.compile(r'(<div class="question">.*?<div class="view-more">.*?</div>)',re.S)
        # list中dict按'id'排序，逆序
        self.content_list.sort(key=lambda obj: obj.get('id'), reverse=True)
        for line_json in self.content_list:  # 对每天的瞎扯操作
            questions=r_question.findall(line_json['body'])
            self.content = self.content + '<div class="day">\n<h1>'+self.titles[line_json['id']] + '</h1>\n'  # 添加一层div，以及一个h1标题，输入日期标题
            for question in questions:
                self.content = self.content + question + '\n</div>\n'
            self.content = self.content + '</div>\n'
    #    with codecs.open('content.html', 'w', 'utf-8') as f:  # 写入到本地文件
    #        f.write(content)
        print('格式转换成功')


    def dl_img(self):  # 下载HTML中链接的图片到本地，便于电子书制作
        print('正在下载图片...（视网络情况可能需要一定时间）')

        def getting():  # 便于多进程处理
            opener = urllib.request.build_opener()
            while(not self.img_url_queue.empty()):
                img_url = self.img_url_queue.get()
                get = urllib.request.Request(
                    url=img_url, headers=headers, method='GET')
                try:
                    img_b = opener.open(get).read()
                except Exception as e:
                    print(e)
                    print('重新下载...')
                    self.img_url_queue.put(img_url)
                    continue
                with open(file_name.split('.')[-2] + '_files/' + img_url.split('/')[-1], 'wb') as f:
                    f.write(img_b)
        if not os.path.exists(file_name.split('.')[-2] + '_files'):
            os.mkdir(file_name.split('.')[-2] + '_files')
        self.multi_thread(20, getting) 
        print('图片全部下载完成！')


    def post_work(self):  # 包括去除作者头像图片，和替换HTML中图片链接，并生成下载图片队列
    #    with codecs.open('content.html', 'r', 'utf-8') as f:
    #        content = f.read()
        self.content = re.sub(r'<img class="avatar".*?>', '', self.content)
        urls = re.findall(r'src="(.*?jpg)"', self.content)
        for url in urls:
            self.img_url_queue.put(url)
            self.content = self.content.replace(
                url, './' + file_name.split('.')[-2] + '_files/' + url.split('/')[-1])
        with codecs.open(file_name, 'w', 'utf-8') as f:  # 写入最终生成HTML文件到本地
            f.write(self.content)
        self.dl_img()
        print('已删除作者头像，并下载全部链接图片！')
    def start(self):
        self.get_list()
        self.get_content()
        self.to_html()
        self.post_work()
if __name__ == '__main__':
    zhihu=Zhihu()
    zhihu.start()
