import scrapy
from bs4 import BeautifulSoup as BS


class CanesSpider(scrapy.Spider):
    name = 'canes'
    allowed_domains = ['hockey-reference.com']
    start_urls = [
        f'http://hockey-reference.com/teams/CAR/{year}_gamelog.html' for year in range(1998, 2020)]

    def parse_individual_game(self, response):
        # #penalty
        # #{team}_skaters has data-stats
        # #{team}_goalies
        year = response.url.split('/')[-1][0:4]
        opp = response.meta.get('opp')
        team = response.meta.get('team')
        date = response.meta.get('date')
        if opp is None or team is None or date is None:
            return

        teams = [team, opp]
        types = ['skaters', 'goalies']

        penalty_table = response.css('table#penalty')[0]
        penalty_table_keys = ['time', 'team', 'player', 'penalty', 'length']
        penalty_dict = dict(
            year=year,
            curr_type='penalty',
            team_one=team,
            team_two=opp,
            date_game=date
        )
        for tr in penalty_table.css('tr'):
            tds = list(tr.css('td'))
            if tds is None or len(tds) == 0:
                continue

            for idx, td in enumerate(tds):
                curr_td = BS(td.extract(), features='lxml').find('td')

                penalty_dict[penalty_table_keys[idx]] = curr_td.text

            yield penalty_dict

        for curr_team in teams:
            for skater_type in types:
                curr_data = dict(
                    year=year,
                    team=curr_team,
                    opp=opp if curr_team == team else team,
                    curr_type=skater_type,
                    date_game=date
                )
                curr_table = response.css(f'table#{curr_team}_{skater_type}')[
                    0].css('tbody')[0]
                for tr in curr_table.css('tr'):
                    for td in tr.css('td'):
                        data = BS(td.extract(), features='lxml').find('td')

                        stat = data.get('data-stat')
                        text = data.text

                        if stat is None or text is None or 'empty' in stat:
                            continue

                        curr_data[stat] = text
                    yield curr_data

    def parse(self, response):
        year = response.url.split('/')[-1][0:4]

        curr_data = dict(
            year=year,
            curr_type='game_log'
        )

        tbody = response.css('tbody')
        for tr in tbody.css('tr'):
            link = None
            opp = None
            date = None
            for td in tr.css('td'):
                data = BS(td.extract(), features='lxml').find('td')

                stat = data.get('data-stat')
                text = data.text

                if stat is None or text is None or 'empty' in stat:
                    continue

                if stat == 'date_game':
                    link = data.find('a').get('href')
                    date = text
                elif stat == 'opp_name':
                    opp = data.get('csk')
                    if opp is not None:
                        opp = opp[0:3]

                curr_data[stat] = text

            if opp is not None and link is not None:
                yield response.follow(link, callback=self.parse_individual_game, meta={'opp': opp, 'team': 'CAR', 'date': date})

            yield curr_data
