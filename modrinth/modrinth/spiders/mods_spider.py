import os
import scrapy
from scrapy_playwright.page import PageMethod
from tqdm import tqdm  # 新增 tqdm 匯入

from modrinth.items import ModsMetadataItem

class ModsSpider(scrapy.Spider):
    name = "mods_spider"
    allowed_domains = ["modrinth.com"]
    base_url = "https://modrinth.com"
    start_url = "https://modrinth.com/mods"
    MAX_PAGES = None
    CURRENT_PAGE = 1
    ALL_LOADERS = ["Fabric", "Forge", "NeoForge", "Quilt", "LiteLoader", "Risugami's ModLoader", "Rift"]    
    
    def start_requests(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Starting Mods Spider...")
        yield scrapy.Request(
            self.start_url,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "#search-results",timeout=60000),
                ]
            },
            callback=self.parse
        )
    
    def next_page(self, response):
        next_page_url = f"{self.start_url}?page={self.CURRENT_PAGE}"
        
        if self.CURRENT_PAGE <= self.MAX_PAGES:
            yield scrapy.Request(
                response.urljoin(next_page_url),
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                        PageMethod("wait_for_selector", "#search-results", timeout=60000),
                    ]
                },
                callback=self.parse,
            )
    

    def parse(self, response):
        if self.MAX_PAGES is None:
            self.MAX_PAGES = int(str(response.xpath(
                '//*[@id="__nuxt"]/div[4]/main/div[5]/section[2]/div/div[2]/div[5]/div[4]/div/a/text()'
            ).get()))
            self.progress_bar = tqdm(total=self.MAX_PAGES, desc="Crawling Pages")
            
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
            
            debug = False
            if debug:
                print(f"Icon URL: {item['icon_url']}")
                print(f"Name: {item['name']}")
                print(f"Mod URL: {item['mod_url']}")
                print(f"Author: {item['author']}")
                print(f"Author URL: {item['author_url']}")
                print(f"Description: {item['description']}")
                print(f"Categories: {item['categories']}")
                print(f"Environment: {item['environment']}")
                print(f"Loader: {item['loaders']}")
                print(f"Downloads: {item['downloads']}")
                print(f"Followers: {item['followers']}")
                print("-" * 50)

            yield item
        
        if self.CURRENT_PAGE < self.MAX_PAGES:
            self.progress_bar.update(1)
            self.CURRENT_PAGE += 1
            yield from self.next_page(response)

    def closed(self, reason):
        if hasattr(self, 'progress_bar'):
            self.progress_bar.close()