import scrapy
from bs4 import BeautifulSoup as BS


class CanesSpider(scrapy.Spider):
    name = 'canes'
    allowed_domains = ['hockey-reference.com']
    start_urls = [
        f'http://hockey-reference.com/teams/CAR/{year}_gamelog.html' for year in range(1998, 2020)]

    def parse(self, response):
        year = response.url.split('/')[-1][0:4]

        curr_data = dict(
            year=year
        )

        tbody = response.css('tbody')
        for tr in tbody.css('tr'):
            for td in tr.css('td'):
                data = BS(td.extract(), features='lxml').find('td')

                stat = data.get('data-stat')
                text = data.text

                if stat is None or text is None or 'empty' in stat:
                    continue

                curr_data[stat] = text

            yield curr_data
