from scrapy.spiders import CrawlSpider

from VideoDownloader.items import VideoDownloaderItem
from VideoDownloader.spiders.tasks import VIDEO_URL


class VideoSpider(CrawlSpider):

    name = "video-spider"
    start_urls = []

    def __init__(self):
        self.start_urls.append(VIDEO_URL)
        super().__init__()

    def parse(self, response):
        video_info = VideoDownloaderItem()
        video_info["name"] = ""
        video_info["url"] = ""
        return video_info
