import logging
import re

from scrapy import Request, FormRequest
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from VideoDownloader.items import VideoDownloaderItem
from VideoDownloader.spiders.settings import VIDEO_URL, LOGIN_URL, USER_NAME, PASSWORD, LOGIN_RESP_URL, VIDEO_LIST_URL


class VideoSpider(CrawlSpider):
    name = "video-spider"
    start_urls = []
    rules = [Rule(LinkExtractor(allow=r"view_video\.php", restrict_xpaths="//ul[@id='videoPlaylist']"), callback="parse_video")]

    login_header = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    }

    def __init__(self):
        self.start_urls.extend(VIDEO_URL)
        self.start_urls.extend(VIDEO_LIST_URL)
        super().__init__()

    def start_requests(self):
        return [Request(url=LOGIN_URL,
                        meta={'cookiejar': 1},
                        callback=self.parse_login)]

    def parse_login(self, response):
        try:
            logging.info("msg=解析登陆页面|url=" + response.url)
            form_data = {}
            for each in response.xpath("//form[@class='js-loginForm']/input[@type='hidden']"):
                key = each.xpath("@name").extract_first()
                value = each.xpath("@value").extract_first()
                form_data.setdefault(key, value)
            form_data.setdefault("username", USER_NAME)
            form_data.setdefault("password", PASSWORD)
            form_data.setdefault("remember_me", "on")
            return [FormRequest.from_response(response,
                                              url=LOGIN_RESP_URL,
                                              method="POST",
                                              meta={"cookiejar": response.meta["cookiejar"]},
                                              headers=self.login_header,
                                              formdata=form_data,
                                              dont_filter=True,
                                              callback=self.after_login)]
        except Exception as ex:
            logging.warning("msg=解析登陆页面失败|url=" + response.url + "|ex=" + str(ex))

    def after_login(self, response):
        logging.info("msg=登陆响应|response=" + response.text)
        while self.start_urls:
            url = self.start_urls.pop()
            logging.info("mag=访问链接|url=" + url)
            if "playlist" in url:
                yield Request(url=url,
                              meta={"cookiejar": response.meta["cookiejar"]})
            elif "view_video" in url:
                yield Request(url=url,
                              meta={"cookiejar": response.meta["cookiejar"]},
                              callback=self.parse_video)

    def parse_video(self, response):
        try:
            logging.info("msg=解析页面|url=" + response.url)
            video_info = VideoDownloaderItem()
            video_info["title"] = response.xpath(
                "//div[@class='title-container']/h1[@class='title']/span[@class='inlineFree']/text()").extract_first()
            video_info["url"] = re.compile(r'"videoUrl":"(https.+?)"').findall(response.text)[0].replace("\\", "")
            video_info["type"] = response.xpath("//video[@class='player-html5']/source/@type").extract_first().split("/")[1]
            return video_info
        except Exception as ex:
            logging.warning("msg=解析页面失败|url=" + response.url + "|ex=" + str(ex))
