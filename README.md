# 知乎日报（瞎扯）爬虫

## 简介

此工具可以将知乎日报中常规栏目（如瞎扯、深夜食堂等）按日期全部爬取下来，保存为HTML文件。借助第三方工具Pandoc，可以将爬取的内容制作为EPUB电子书等。

![Xiache EPUB Screenshot][xiache_epub_screenshot]

## 使用示例

示例如example.py中所示。

### 获取栏目ID

```python
zhihu = Zhihu()
# 显示栏目ID和名称
zhihu.get_section()
```

可以得到栏目ID（供后续使用），如：

```text
1 深夜惊奇
2 瞎扯
19 这里是广告 
26 读读日报推荐 
28 放映机 
29 大误 
33 《职人介绍所》
...
```

### 爬取内容

```python
zhihu = Zhihu()
zhihu.start(section='2', start_date='20170401', end_date='20170910')
```

`section`即栏目ID，`start_date`即指定开始日期，`end_data`即指定结束日期。运行完成后会生成final.html文件即爬取的内容，以及final_files文件夹即图片等文件。

## 制作EPUB电子书

下面以制作瞎扯的电子书为例。

### 安装Pandoc

可以参考[Pandoc官网][https://pandoc.org/]的安装指引。如在macOS下可以通过homebrew安装：`brew install pandoc`。

### 制作电子书

在命令行下切换目录到当前目录下。运行

```bash
pandoc final.html --epub-stylesheet=resources/render.css -o xiache.epub
```

即可得到xiache.epub电子书。

[xiache_epub_screenshot]: xiache_epub_screenshot.png
