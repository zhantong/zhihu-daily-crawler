"""
	利用知乎日报API爬取“瞎扯”栏目所有文章。
	大体为首先获取全部瞎扯URL的后缀（API循环），然后逐个访问，并存储到本地文件。
	API采用JSON格式。
"""
import json
import queue
import urllib.request
import codecs
q = queue.Queue()  # URL后缀队列
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
    while(1):
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


def get_xiache_content():  # 获取瞎扯内容
    for item in xiache_list:
        q.put(str(item['id']))  # 瞎扯URL后缀
    url = 'http://news-at.zhihu.com/api/4/story/'  # 此URL与瞎扯URL后缀拼接
    opener = urllib.request.build_opener()
    while(not q.empty()):
        xiache_id = q.get()
        get = urllib.request.Request(
            url=url + xiache_id, headers=headers, method='GET')
        con = opener.open(get).read().decode('utf-8')
        with codecs.open('xiache.txt', 'a', 'utf-8') as f:  # 写入到本地文件
            f.write(con)
            f.write('\n')
        print(xiache_id, 'done')

if __name__ == '__main__':
    get_xiache_list()
    get_xiache_content()
