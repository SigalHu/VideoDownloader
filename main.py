import logging
import os
import signal
import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from VideoDownloader.spiders import settings
from VideoDownloader.spiders.video_spider import VideoSpider


class VideoDownloadProcessor(FileSystemEventHandler):

    def __init__(self):
        FileSystemEventHandler.__init__(self)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
        self._logger = logging.getLogger(self.__class__.__name__)
        self._create_pid_file(os.path.dirname(__file__))
        self._register_signal()
        self.__last_modify_timestamp = time.time()
        self.__observer = Observer()

    def __del__(self):
        if self.__pid_file and os.path.isfile(self.__pid_file):
            os.remove(self.__pid_file)
        if self.__observer.is_alive():
            self.__observer.stop()

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

    def on_created(self, event):
        self._logger.info("Received the file system event: created %s", event.src_path)
        self.__last_modify_timestamp = time.time()

    def on_modified(self, event):
        self._logger.info("Received the file system event: modified %s", event.src_path)
        self.__last_modify_timestamp = time.time()

    def process(self):
        self.__watch_dir()
        self.__run_scrapy()

    def __watch_dir(self):
        if not os.path.exists(settings.SAVE_PATH):
            os.makedirs(settings.SAVE_PATH)
        self.__observer.schedule(self, settings.SAVE_PATH, True)
        self.__observer.start()

    def __run_scrapy(self):
        while True:
            self.__last_modify_timestamp = time.time()
            self._logger.info("Start to process scrapy!")
            proc = subprocess.Popen(["scrapy", "crawl", VideoSpider.name])
            self.__wait_scrapy(proc, 60)
            if proc.poll() is not None:
                self._logger.info("Finished to process scrapy, all items have been handled!")
                break
            try:
                while proc.poll() is None:
                    if self.__scrapy_timeout():
                        self._logger.info("Timeout to wait scrapy!")
                        self.__stop_scrapy(proc)
                        break
                    self.__wait_scrapy(proc, 60)
            except:
                self._logger.exception("Error to process scrapy!")
                self.__stop_scrapy(proc)
                break

    def __wait_scrapy(self, proc, sec=None):
        try:
            proc.wait(sec)
        except SignalException as ex:
            raise ex
        except:
            pass

    def __stop_scrapy(self, proc):
        self._logger.info("Start to stop scrapy...")
        proc.send_signal(signal.SIGKILL)
        while proc.poll() is None:
            self.__wait_scrapy(proc, 10)
        self._logger.info("Succeed to stop scrapy!")

    def __scrapy_timeout(self) -> bool:
        return time.time() - self.__last_modify_timestamp >= 10 * 60


class SignalException(Exception):
    pass


if __name__ == '__main__':
    VideoDownloadProcessor().process()
