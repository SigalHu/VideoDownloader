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
    download_header = {
        "Accept-Encoding": "identity;q=1, *;q=0",
        "Range": None,
        "Referer": None,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36 115Browser/8.6.2"
    }

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

        content_offset = 0
        content_length = 1024 * 1024 * 10
        total_length = None
        self.download_header["Referer"] = video_url
        while True:
            self.download_header["Range"] = "bytes=%d-%d" % (content_offset, content_offset + content_length)
            resp = requests.get(video_url, stream=True, headers=self.download_header)
            resp_length = int(resp.headers["Content-Length"])
            if total_length is None:
                total_length = int(resp.headers["Content-Range"].split("/")[1])

            with open(file_name, 'ab') as file:
                file.write(resp.content)
                file.flush()

            content_offset += resp_length
            if content_offset >= total_length:
                break

    def get_valid_name(self, expected_file_name, instead_str=' '):
        valid_name = re.compile(r'[/\\:*?"<>|]').sub(instead_str, expected_file_name)
        return valid_name.strip(' ')
