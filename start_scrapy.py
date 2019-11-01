# encoding=utf-8
"""
@author huxujun
@date 2019/11/2
"""

from scrapy import cmdline

if __name__ == '__main__':
    cmdline.execute("scrapy crawl video-spider".split())
