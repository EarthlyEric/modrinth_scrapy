# Modrinth Scrapy
A simple web scraper for the Mods on Modrinth. It based on scrapy

## Installation
Please install uv first. Use uv to install the required packages:
```bash
uv sync
```

Install and start tor proxy via docker.
```bash
docker compose up -d 
```
## Usage
```bash
scrapy crawl mods_spider -o mods.csv 
```
## License
Distributed under the MIT License.
