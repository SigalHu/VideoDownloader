# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import os
import re

import requests

from VideoDownloader.spiders.settings import SAVE_PATH


class VideoDownloaderPipeline(object):
    def process_item(self, item, spider):
        file_path = item["title"] + "." + item["type"]
        try:
            file_path = self.get_valid_name(file_path, " ")
            file_path = os.path.join(SAVE_PATH, file_path)
            file_path = os.path.abspath(file_path)

            logging.info("msg=开始下载|path=" + file_path + "|url=" + item["url"])
            self.download_video(item["url"], file_path)
        except Exception as ex:
            logging.warning("msg=下载失败|path=" + file_path + "|ex=" + str(ex))
        else:
            logging.info("msg=下载完成|path=" + file_path)
        return item

    def download_video(self, video_url, file_name):
        if os.path.exists(file_name):
            return
        path = os.path.dirname(file_name)
        if not os.path.exists(path):
            os.mkdir(path)
        resp = requests.get(video_url, stream=True)
        with open(file_name, 'wb') as file:
            file.write(resp.content)
            file.flush()

    def get_valid_name(self, expected_file_name, instead_str=' '):
        valid_name = re.compile(r'[/\\:*?"<>|]').sub(instead_str, expected_file_name)
        return valid_name.strip(' ')
