'''
Created on Sep 4, 2013

@author: anuvrat
'''
import pickle
import datetime
import urllib.request
from bs4 import BeautifulSoup
import re

def loadState():
    try:
        state_file = open( "state_dump", "rb" )
        apps_discovered = pickle.load( state_file )
        apps_pending = pickle.load( state_file )
        state_file.close()
        print( "Pending = ", len( apps_pending ), " Discovered = ", len( apps_discovered ) )
        return apps_discovered, apps_pending
    except IOError:
        print( "A fresh start ..." )
        return [], []

character_encoding = 'utf-8'
apps_discovered, apps_pending = loadState()

def saveState():
    state_file = open( "state_dump", "wb" )
    pickle.dump( apps_discovered, state_file )
    pickle.dump( apps_pending, state_file )
    state_file.close()

def getPageAsSoup(url, cookie):
    opener = urllib.request.build_opener()
    opener.addheaders.append( ( 'Cookie', cookie ) )
    try:
        response = opener.open( url )
    except urllib.error.HTTPError as e:
        print( "Error fetching the page ", url, e )
        return None
    return BeautifulSoup( response.read() )

def getApps(url, cookie):
    page = 1
    apps_found = []
    while(True):
        print( url, page )
        content = getPageAsSoup( url + "?page=" + str( page ), cookie )
        apps_on_page = []
        for link_div in content.find_all( 'a', href = re.compile( '^/apps/' ) ):
            app_page = getPageAsSoup( 'https://droidmeter.com' + link_div.get( 'href' ), cookie )
            if not app_page: continue
            for app_link_div in app_page.find_all( 'a', href = re.compile( '^https://market.android.com' ) ):
                apps_on_page.append( app_link_div.getText() )
        if apps_on_page == []: break
        apps_found.extend( apps_on_page )
        page += 1

    return apps_found

if __name__ == '__main__':
    crawl_date = datetime.datetime.strptime( '2013-09-01', '%Y-%m-%d' )
    cookie = '_market_bot_site_session=BAh7CEkiD3Nlc3Npb25faWQGOgZFRkkiJTgxOWUxNGQwOWIxNWYyZjk1YmMwYzI2MzFjM2ZmZDA1BjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMUo1QUlqNEU5UmdWZi8yWTdkdDdicVJOT3BuZTQ0YUNUVUxDcVlxQnJ2UEU9BjsARkkiGXdhcmRlbi51c2VyLnVzZXIua2V5BjsAVFsISSIJVXNlcgY7AEZbBmkCUgQiIiQyYSQxMCQ1dkJhUHJPWFZzUjBqOWhGeW5hUElP--dd5fa12a122cb28271c88db53ef5ce484ac2e90a'
    links = ['https://droidmeter.com/boards/top-grossing',
             'https://droidmeter.com/boards/featured',
             'https://droidmeter.com/boards/featured-tablet',
             'https://droidmeter.com/boards/movers-and-shakers',
             'https://droidmeter.com/boards/new-top-selling-free',
             'https://droidmeter.com/boards/new-top-selling-paid',
             'https://droidmeter.com/boards/top-selling-free',
             'https://droidmeter.com/boards/top-selling-paid' ]

    for link in links:
        link = '/'.join( [link, str( crawl_date.year ), str( crawl_date.month ), str( crawl_date.day )] )
        new_apps = getApps( link, cookie )
        print( len( apps_pending ), len( new_apps ) )
        apps_pending.extend( x for x in new_apps if x not in apps_pending and x not in apps_discovered )
        print( len( apps_pending ) )
        saveState()
