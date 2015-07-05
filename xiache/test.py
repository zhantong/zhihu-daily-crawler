import json
import codecs
import re
header={}
def trans_header(date,title):
	trans=date[0:4]+'年'+str(int(date[4:6]))+'月'+str(int(date[6:8]))+'日'+'  '+title
	return trans
with open('xiache_list.txt','r') as f:
	for line in f:
		line_json=json.loads(line)
		for item in line_json:
			header[item['id']]=trans_header(item['date'],item['title'])
content=''
with codecs.open('xiache.txt','r','utf-8') as f:
	for line in f:
		line_json=json.loads(line)
		r=re.findall('(<div class="question">.*?<div class="view-more">.*?</div>)',line_json['body'],re.S)
		content=content+'<div class="day">\n<h1>'+header[line_json['id']]+'</h1>\n'
		for question in r:
			content=content+question+'\n</div>\n'
		content=content+'</div>\n'
with codecs.open('conten.html','w','utf-8') as f:
	f.write(content)