# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import os
import re
from time import sleep

import requests
from scrapy.utils.project import get_project_settings

from VideoDownloader.spiders.settings import SAVE_PATH


class VideoDownloaderPipeline(object):
    download_header = {
        "Accept-Encoding": "identity;q=1, *;q=0",
        "Range": None,
        "Referer": None,
        # "Connection": "Close",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36 115Browser/8.6.2"
    }
    proxy = {}

    def __init__(self):
        settings = get_project_settings()
        self.proxy = settings.get("PROXY", {})
        super().__init__()

    def process_item(self, item, spider):
        file_path = item["title"] + "." + item["type"]
        try:
            file_path = self.get_valid_name(file_path, " ")
            file_path = os.path.join(SAVE_PATH, file_path)
            file_path = os.path.abspath(file_path)

            retry_count = 0
            while retry_count < 6:
                try:
                    logging.info("msg=开始下载|retry=%d|path=%s|url=%s" % (retry_count, file_path, item["url"]))
                    self.download_video(item["url"], file_path)
                    break
                except Exception as ex:
                    logging.warning("msg=下载异常|path=%s|url=%s|ex=%s" % (file_path, item["url"], str(ex)))
                    retry_count += 1
                    if retry_count < 6:
                        sleep(2**retry_count)
            if retry_count == 6:
                spider.start_urls.append(item["url"])
                logging.warning("msg=下载失败|path=%s" % file_path)
            else:
                logging.info("msg=下载完成|path=%s" % file_path)
        except:
            logging.exception("msg=下载失败|path=%s" % file_path)
        return item

    def download_video(self, video_url, file_name):
        path = os.path.dirname(file_name)
        if not os.path.exists(path):
            os.mkdir(path)

        content_offset = 0
        if os.path.exists(file_name):
            content_offset = os.path.getsize(file_name)

        content_length = 1024 * 1024 * 10
        total_length = None
        self.download_header["Referer"] = video_url
        with requests.session() as s:
            s.headers = self.download_header
            s.proxies = self.proxy
            s.stream = True
            while True:
                s.headers["Range"] = "bytes=%d-%d" % (content_offset, content_offset + content_length)
                resp = s.get(video_url, timeout=10)
                if not resp.ok:
                    if resp.status_code == 416:
                        return
                    continue
                resp_length = int(resp.headers["Content-Length"])
                resp_range = resp.headers["Content-Range"]
                if total_length is None:
                    total_length = int(resp_range.split("/")[1])
                resp_offset = int(re.compile(r"bytes (\d+)-").findall(resp_range)[0])
                if resp_offset != content_offset:
                    continue

                with open(file_name, 'ab') as file:
                    file.write(resp.content)
                    file.flush()

                content_offset += resp_length
                if content_offset >= total_length:
                    break

    def get_valid_name(self, expected_file_name, instead_str=' '):
        valid_name = re.compile(r'[/\\:*?"<>|]+').sub(instead_str, expected_file_name)
        return valid_name.strip(' ')
