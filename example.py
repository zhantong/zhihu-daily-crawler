from Zhihu import Zhihu

if __name__ == '__main__':
    zhihu = Zhihu()
    # 显示栏目ID和名称
    # zhihu.get_section()
    # 指定栏目ID、开始日期、结束日期，即可开始抓取内容。生成的html为final.html，对应图片在final_files文件夹中。
    zhihu.start(section='2', start_date='20170401', end_date='20170910')
