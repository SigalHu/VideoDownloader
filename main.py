import logging
import os
import signal
import subprocess

from scrapy import cmdline
from scrapy.crawler import CrawlerProcess

from VideoDownloader.spiders.video_spider import VideoSpider


class VideoDownloadProcessor(object):

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
        self._logger = logging.getLogger(self.__class__.__name__)
        self._create_pid_file()
        self._register_signal()

    def __del__(self):
        if self.__pid_file and os.path.isfile(self.__pid_file):
            os.remove(self.__pid_file)

    @staticmethod
    def _register_signal():
        signal.signal(signal.SIGTERM, VideoDownloadProcessor.__signal_handler)
        signal.signal(signal.SIGINT, VideoDownloadProcessor.__signal_handler)

    @staticmethod
    def __signal_handler(signal_num, frame):
        raise SignalException("Received signal {}".format(signal_num))

    def _create_pid_file(self, output="."):
        self.__pid_file = os.path.join(output, "pid.txt")
        self._logger.info("Create the %s", self.__pid_file)
        with open(self.__pid_file, "w") as f:
            f.write("{}\n".format(os.getpid()))

    def process(self):
        self.__run_scrapy()

    def __run_scrapy(self):
        proc = CrawlerProcess()
        proc.crawl(VideoSpider)
        proc.start()
        print()


class SignalException(Exception):
    pass


if __name__ == '__main__':
    # VideoDownloadProcessor().process()
    cmdline.execute("scrapy crawl video-spider".split())
