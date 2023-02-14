import requests
from datetime import datetime, timezone
from seleniumwire import webdriver
import os

"""
may break on linux due to libc implementation can be changed
to %-m or %-d to remove leading 0s, example shows them without,
description shows them with.
"""
def convertDateTime(dateTime):
    return dateTime.astimezone(timezone.utc).strftime("%Y-%#m-%#d %H:%M")

def getBwinToken():
    '''
    Get Bwin token to access the API
    '''
    if os.path.exists('tokens.txt'):
        with open('tokens.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                site, token = line.split('=')
                if site == 'bwin':
                    print(f'Local token retrieved: {token}')
                    return token
    print('Retrieving bwin token...')
    options = webdriver.FirefoxOptions()
    options.add_argument('log-level=3')
    options.add_argument('--headless')
    options.add_argument('--disable-extensions')
    driver = webdriver.Firefox(options=options)
    driver.get('https://sports.bwin.com/en/sports')
    for request in driver.requests:
        if request.response and 'x-bwin-accessid=' in request.url:
            token = request.url.split('x-bwin-accessid=')[1].split('&')[0]
            with open('tokens.txt', 'a+') as file:
                file.write(f'bwin={token}')
            break
    driver.quit()
    print(f'Token retrieved: {token}')
    return token

def parseBwinAPI(params):
    '''
    Parse Bwin API and sort data, can be used with any params.
    '''
    token = getBwinToken()
    if not token:
        return
    url = (f'https://cds-api.bwin.com/bettingoffer/fixtures?x-bwin-accessid={token}&lang=en&country=GB&userCountry=GB&fixtureTypes=Standard&state=Latest&offerMapping=Filtered&offerCategories=Gridable&fixtureCategories=Gridable&{params}&skip=0&take=1000&sortBy=Tags')
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'})
    fetched = r.json()
    fixtures = fetched['fixtures']
    bwinData = []
    for fixture in fixtures:
        if fixture['stage'] == 'Live':
            continue
        odds = []
        participants = fixture['participants']
        name = ' vs '.join(map(lambda x: x['name']['value'], participants))
        games = fixture['games']
        for game in games:
            odds_type = game['name']['value']
            if odds_type not in ['Match Winner']:
                continue
            for result in game['results']:
                odds.append(result['odds'])
            updateTime = convertDateTime(datetime.now())
            timeDate = convertDateTime(datetime.strptime(f"{fixture['startDate']}"[:-1], '%Y-%m-%dT%H:%M:%S'))
            bwinData.append({"eventName": name, "player1": list(fixture['participants'])[0]['name']['value'], "player2": list(fixture['participants'])[1]['name']['value'], "player1_odds": odds[0], "player2_odds": odds[1], "eventDate": timeDate, "lastUpdate": updateTime})
    with open('bwinData.json', 'a+') as file:
        file.write(f'{bwinData}')
    return

#parse any params found on the bwin api.
parseBwinAPI('')