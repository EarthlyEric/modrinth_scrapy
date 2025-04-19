import os
import scrapy
from scrapy_playwright.page import PageMethod
from tqdm import tqdm

from modrinth.items import ModsMetadataItem

class ModsSpider(scrapy.Spider):
    name = "mods_spider"
    allowed_domains = ["modrinth.com"]
    base_url = "https://modrinth.com"
    start_url = "https://modrinth.com/mods"
    MAX_PAGES = None
    progress_file = "progress.txt"
    ALL_LOADERS = ["Fabric", "Forge", "NeoForge", "Quilt", "LiteLoader", "Risugami's ModLoader", "Rift"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.CURRENT_PAGE = self.load_progress()

    def load_progress(self):
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, "r") as f:
                    page = int(f.read().strip())
                    return page + 1
            except Exception as e:
                print("Failed to load progress: %s", e)
        return 1

    def save_progress(self):
        try:
            with open(self.progress_file, "w") as f:
                f.write(str(self.CURRENT_PAGE))
        except Exception as e:
            print("Failed to save progress: %s", e)

    def start_requests(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Starting Mods Spider…")
        yield scrapy.Request(
            self.start_url,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "#search-results", timeout=60000),
                ]
            },
            callback=self.parse,
            errback=self.errback
        )

    def next_page(self):
        next_page_url = f"{self.start_url}?page={self.CURRENT_PAGE}"
        yield scrapy.Request(
            next_page_url,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "#search-results", timeout=60000),
                ]
            },
            callback=self.parse,
            errback=self.errback
        )

    def parse(self, response):
        if self.MAX_PAGES is None:
            max_page_text = response.xpath(
                '//*[@id="__nuxt"]/div[4]/main/div[5]/section[2]/div/div[2]/div[5]/div[4]/div/a/text()'
            ).get()
            self.MAX_PAGES = int(max_page_text) if max_page_text and max_page_text.isdigit() else 1
            self.progress_bar = tqdm(total=self.MAX_PAGES, desc="Crawling Pages")
            if self.CURRENT_PAGE > 1:
                self.progress_bar.update(self.CURRENT_PAGE - 1)

        mod_list = response.xpath('//*[@id="search-results"]//article[contains(@class, "project-card")]')
        for mod in mod_list:
            item = ModsMetadataItem()
            item['icon_url'] = mod.xpath('.//a[contains(@class, "icon")]/img/@src').get()
            item['name'] = mod.xpath('.//div[contains(@class, "title")]/a/h2/text()').get()
            item['mod_url'] = self.base_url + mod.xpath('.//div[contains(@class, "title")]/a/@href').get()
            item['author'] = mod.xpath('.//div[contains(@class, "title")]/p/a/text()').get()
            item['author_url'] = self.base_url + mod.xpath('.//div[contains(@class, "title")]/p/a/@href').get()
            item['description'] = mod.xpath('.//p[contains(@class, "description")]/text()').get()

            tags_list = mod.xpath('.//div[contains(@class, "categories")]/span/text()').getall()
            item['environment'] = tags_list[0] if tags_list else None
            categories = []
            loaders = []
            for tag in tags_list[1:]:
                if tag in self.ALL_LOADERS:
                    loaders.append(tag)
                else:
                    categories.append(tag)
            item['categories'] = categories
            item['loaders'] = loaders

            item['downloads'] = mod.xpath('.//div[contains(@class,"stats")]/div[contains(@class,"stat")][1]//strong/text()').get()
            item['followers'] = mod.xpath('.//div[contains(@class,"stats")]/div[contains(@class,"stat")][2]//strong/text()').get()
            
            yield item

        self.save_progress()

        if self.CURRENT_PAGE < self.MAX_PAGES:
            self.progress_bar.update(1)
            self.CURRENT_PAGE += 1
            yield from self.next_page()

    def errback(self, failure):
        self.logger.error("Request failed: %s", failure.request.url)
        self.logger.error(repr(failure))
        self.save_progress()
        if self.MAX_PAGES is None:
            print("Retrying the first page request...")
            yield scrapy.Request(
                self.start_url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "#search-results", timeout=60000),
                    ]
                },
                callback=self.parse,
                errback=self.errback
            )
        elif self.CURRENT_PAGE < self.MAX_PAGES:
            print("Resuming to page %s", self.CURRENT_PAGE + 1)
            self.CURRENT_PAGE += 1
            yield from self.next_page()

    def closed(self, reason):
        if hasattr(self, 'progress_bar'):
            self.progress_bar.close()
        print.info("Spider closed. Current page: %s", self.CURRENT_PAGE)