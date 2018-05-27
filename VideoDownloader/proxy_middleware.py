import logging
import re

from scrapy.utils.project import get_project_settings


class ProxyMiddleware(object):
    proxy = {}

    def __init__(self):
        settings = get_project_settings()
        self.proxy = settings.get("PROXY", {})
        super().__init__()

    def process_request(self, request, spider):
        try:
            key = re.compile(r"^(https?):", flags=re.IGNORECASE).findall(request.url)[0].lower()
            if self.proxy.__contains__(key):
                request.meta['proxy'] = self.proxy.get(key)
            else:
                logging.info("msg=代理失败|key=%s" % key)
        except Exception as ex:
            logging.warning("msg=代理失败|ex=%s" % str(ex))
