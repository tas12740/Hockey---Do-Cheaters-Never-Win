import scrapy
from bs4 import BeautifulSoup as BS


class OthersSpider(scrapy.Spider):
    name = 'all'
    allowed_domains = ['hockey-reference.com']
    teams = ['ANA', 'PHX', 'BOS', 'BUF', 'CGY', 'CAR', 'CHI', 'COL', 'CBJ', 'DAL', 'DET', 'EDM', 'FLA', 'LAK', 'MIN', 'MTL', 'NSH', 'NJD', 'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'SJS', 'STL', 'TBL', 'TOR', 'VAN', 'VEG', 'WSH', 'WPG',
             # 'HAM', 'MTM', 'MTW', 'NYA', 'OTS', 'PHQ', 'PTP', 'STE', 'CLE', 'CGS', 'OAK', 'BRO',
             'ARI', 'ATL', 'HAR', 'ATF', 'MNS', 'CLR', 'KCS', 'DTF', 'DTC', 'TRS', 'TRA', 'WIN', 'MDA', 'CBH', 'QUE']
    start_urls = [
        f'http://hockey-reference.com/teams/{team}/{year}_gamelog.html' for team in teams for year in range(1917, 2020)]

    def parse(self, response):
        year = response.url.split('/')[-1][0:4]
        team = response.url.split('/')[-2]

        curr_data = dict(
            year=year,
            team=team
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
