import json
import queue
import urllib.request
import codecs
q=queue.Queue()

def get_xiache_list():
	headers={
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'
	}
	url='http://news-at.zhihu.com/api/4/section/2'
	opener = urllib.request.build_opener()


	get=urllib.request.Request(url=url,headers=headers,method='GET')
	con=opener.open(get).read().decode('utf-8')
	con=json.loads(con)
	t=json.dumps(con['stories'],ensure_ascii=False,sort_keys=True)
	with open('xiache_list.txt','a') as f:
		f.write(t)
		f.write('\n')
	print(con['timestamp'])
	while(1):
		try:
			time=con['timestamp']
		except Exception:
			print('done')
			break
		print(time)
		get=urllib.request.Request(url=url+'/before/'+str(time),headers=headers,method='GET')
		try:
			con=opener.open(get).read().decode('utf-8')
		except Exception as e:
			print(e)
			break
		con=json.loads(con)
		t=json.dumps(con['stories'],ensure_ascii=False,sort_keys=True)
		with open('xiache_list.txt','a') as f:
			f.write(t)
			f.write('\n')

def gether_xiache_list():
	xiache_list=[]
	with open('xiache_list.txt','r') as f:
		for line in f:
			t=json.loads(line)
			xiache_list.extend(t)
	with open('xiache_list_gether.txt','w') as f:
		f.write(json.dumps(xiache_list,ensure_ascii=False,sort_keys=True))

def get_xiache_content():
	with open('xiache_list_gether.txt','r') as f:
		xiache_list=json.loads(f.read())
	for item in xiache_list:
		q.put(str(item['id']))
	headers={
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'
	}
	url='http://news-at.zhihu.com/api/4/story/'
	opener = urllib.request.build_opener()

	while(not q.empty()):
		xiache_id=q.get()
		get=urllib.request.Request(url=url+xiache_id,headers=headers,method='GET')
		con=opener.open(get).read().decode('utf-8')
		with codecs.open('xiache.txt','a','utf-8') as f:
			f.write(con)
			f.write('\n')
		print(xiache_id,'done')

if __name__ == '__main__':
	get_xiache_list()
	gether_xiache_list()
	get_xiache_content()
