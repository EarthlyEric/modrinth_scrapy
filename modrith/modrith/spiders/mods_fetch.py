import scrapy


class ModsFetchSpider(scrapy.Spider):
    name = "mods_fetch"
    allowed_domains = ["modrith.com"]
    start_urls = ["https://modrinth.com/mods"]

    def parse(self, response):
        pass
