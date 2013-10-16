'''
Created on Aug 28, 2013

@author: anuvrat
'''

from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import codecs
import json
import pickle
from datetime import datetime

def loadState():
    try:
        state_file = open( "state_dump", "rb" )
        apps_discovered = pickle.load( state_file )
        apps_pending = pickle.load( state_file )
        #apps_count = pickle.load( state_file )
        state_file.close()
        print( "Pending = ", len( apps_pending ), " Discovered = ", len( apps_discovered ) )
        return apps_discovered, apps_pending
    except IOError:
        print( "A fresh start ..." )
        return [], []

character_encoding = 'utf-8'
apps_discovered, apps_pending = loadState()
count_offset = len( apps_discovered )

start_time = datetime.now()

def getPageAsSoup( url, post_values ):
    if post_values:
        data = urllib.parse.urlencode( post_values )
        data = data.encode( character_encoding )
        req = urllib.request.Request( url, data )
    else:
        req = url
    try:
        response = urllib.request.urlopen( req )
    except urllib.error.HTTPError as e:
        print( "HTTPError with: ", url, "\t", e )
        return None
    the_page = response.read()
    soup = BeautifulSoup( the_page )

    return soup

def openResultFiles(all_categories):
    fileHandlers = {}
    for category in all_categories:
        fileHandler = codecs.open( '_'.join( ["apps", category.lower()] ), 'ab', character_encoding, buffering = 0 )
        fileHandlers[category] = fileHandler
    return fileHandlers

def closeResultFiles(fileHandlers):
    for v in fileHandlers.values():
        v.close()

def reportProgress():
    current_time = datetime.now()
    elapsed = current_time - start_time
    v = ( ( len( apps_discovered ) - count_offset ) / elapsed.seconds ) * 60
    t = len( apps_pending ) / v if v > 0 else 0
    print( "Pending = ", len( apps_pending ), " Discovered = ", len( apps_discovered ), " Velocity = ", str( v ), " apps per minute and time remaining in minutes = ", str( t ) )

def saveState():
    state_file = open( "state_dump", "wb" )
    pickle.dump( apps_discovered, state_file )
    pickle.dump( apps_pending, state_file )
    state_file.close()
    reportProgress()

def getAppDetails(app_url):
    if app_url in apps_discovered:
        # print( "Skip because already parsed: ", app_url )
        return None

    g_app_url = 'https://play.google.com' + app_url
    app_details = {}

    app_details['app_url'] = g_app_url

    soup = getPageAsSoup( g_app_url, None )
    if not soup: return None

    apps_discovered.append( app_url )

    print( g_app_url )
    title_div = soup.find( 'div', {'class':'document-title'} )
    app_details['title'] = title_div.find( 'div' ).get_text().strip()

    subtitle = soup.find( 'a', {'class' : 'document-subtitle primary'} )
    app_details['developer'] = subtitle.get_text().strip()
    app_details['developer_link'] = subtitle.get( 'href' ).strip()

    price_buy_span = soup.find( 'span', {'class' : 'price buy'} )
    price = price_buy_span.find_all( 'span' )[-1].get_text().strip()
    price = price[:-4].strip() if price != 'Install' else 'Free' 
    app_details['price'] = price

    rating_value_meta = soup.find( 'meta', {'itemprop' : 'ratingValue'} )
    app_details['rating'] = rating_value_meta.get( 'content' ).strip()

    reviewers_count_meta = soup.find( 'meta', {'itemprop' : 'ratingCount'} )
    app_details['reviewers'] = reviewers_count_meta.get( 'content' ).strip()

    num_downloads_div = soup.find( 'div', {'itemprop' : 'numDownloads'} )
    if num_downloads_div: app_details['downloads'] = num_downloads_div.get_text().strip()

    date_published_div = soup.find( 'div', {'itemprop' : 'datePublished'} )
    app_details['date_published'] = date_published_div.get_text().strip()

    operating_systems_div = soup.find( 'div', {'itemprop' : 'operatingSystems'} )
    app_details['operating_system'] = operating_systems_div.get_text().strip()

    content_rating_div = soup.find( 'div', {'itemprop' : 'contentRating'} )
    app_details['content_rating'] = content_rating_div.get_text().strip()

    category_span = soup.find( 'span', {'itemprop' : 'genre'} )
    app_details['category'] = category_span.get_text()

    for dev_link in soup.find_all( 'a', {'class' : 'dev-link'} ):
        if dev_link.get_text().strip() == "Email Developer":
            app_details['email'] = dev_link.get( 'href' ).strip()[7:]
        elif dev_link.get_text().strip() == "Visit Developer's Website":
            app_details['dev_website'] = dev_link.get( 'href' ).strip()

    badge_span = soup.find( 'span', {'class' : 'badge-title'} )
    if badge_span: app_details['badge'] = badge_span.get_text().strip()

    for more_apps in soup.find_all( 'div', {'data-short-classes' : 'card apps square-cover tiny no-rationale'} ):
        more_app_url = more_apps.find( 'a', {'class' : 'card-click-target'} ).get( 'href' )
        if more_app_url not in apps_discovered and more_app_url not in apps_pending: apps_pending.append( more_app_url )

    return app_details

def getTopAppsData( url, start, num, app_type ):
    values = {'start' : start,
              'num': num,
              'numChildren':'0',
              'ipf': '1',
              'xhr': '1'}
    soup = getPageAsSoup( url, values )
    if not soup: return [], []

    apps = []
    skipped_apps = []
    for div in soup.findAll( 'div', {'class' : 'details'} ):
        title = div.find( 'a', {'class':'title'} )
        try:
            app_details = getAppDetails( title.get( 'href' ) )
        except AttributeError:
            pass
        if app_details: apps.append( app_details )
        else: skipped_apps.append( title.get( 'href' ) )

    return apps, skipped_apps

def getApps( url ):
    previous_apps = []
    previous_skipped_apps = []
    start_idx = 0
    size = 100
    while(True):
        apps, skipped_apps = getTopAppsData( url, start_idx, size, app_type )
        if apps == previous_apps and skipped_apps == previous_skipped_apps: break
        for app in apps:
            if app['category'].upper() not in fileHandlers:
                fileHandlers[app['category'].upper()] = codecs.open( '_'.join( ["apps", app['category'].lower()] ), 'ab', character_encoding, buffering = 0 )
            fileHandler = fileHandlers[app['category'].upper()]
            try:
                fileHandler.write( json.dumps( app ) + "\n" )
            except Exception as e:
                print( e )
        previous_apps = apps
        previous_skipped_apps = skipped_apps
        start_idx += size
        saveState()

categories = ['BOOKS_AND_REFERENCE', 'BUSINESS', 'COMICS', 'COMMUNICATION', 'EDUCATION', 'ENTERTAINMENT', 'FINANCE', 'HEALTH_AND_FITNESS', 'LIBRARIES_AND_DEMO', 'LIFESTYLE', 'APP_WALLPAPER', 'MEDIA_AND_VIDEO', 'MEDICAL', 'MUSIC_AND_AUDIO', 'NEWS_AND_MAGAZINES', 'PERSONALIZATION', 'PHOTOGRAPHY', 'PRODUCTIVITY', 'SHOPPING', 'SOCIAL', 'SPORTS', 'TOOLS', 'TRANSPORTATION', 'TRAVEL_AND_LOCAL', 'WEATHER', 'ARCADE', 'BRAIN', 'CARDS', 'CASUAL', 'GAME_WALLPAPER', 'RACING', 'SPORTS_GAMES', 'GAME_WIDGETS']
app_types = ['free', 'paid']

fileHandlers = openResultFiles( categories )

for category, app_type in [( x, y ) for x in categories for y in app_types]:
    print( "Type = ", app_type, " Cateory = ", category )
    url = 'https://play.google.com/store/apps/category/' + category + '/collection/topselling_' + app_type
    getApps( url )

top_urls = ['https://play.google.com/store/apps/collection/topselling_paid_game',
            'https://play.google.com/store/apps/collection/topselling_free',
            'https://play.google.com/store/apps/collection/topselling_paid',
            'https://play.google.com/store/apps/collection/topgrossing',
            'https://play.google.com/store/apps/collection/topselling_new_paid_game',
            'https://play.google.com/store/apps/collection/topselling_new_free',
            'https://play.google.com/store/apps/collection/topselling_new_paid']
for url in top_urls:
    print( "Crawl collection - ", url )
    getApps( url )

errorUrls = codecs.open('_'.join(["apps", "error"]), 'ab', character_encoding, buffering = 0)
count = 100
while apps_pending:
    if count == 0:
        saveState()
        count = 100
    count = count - 1

    app = apps_pending.pop()
    try:
        app_data = getAppDetails( app )
    except AttributeError:
        pass
    if not app_data: 
      continue
    if app_data['category'].upper() not in fileHandlers:
        fileHandlers[app_data['category'].upper()] = codecs.open( '_'.join( ["apps", app_data['category'].lower()] ), 'ab', character_encoding, buffering = 0 )
    fileHandler = fileHandlers[app_data['category'].upper()]
    try:
        fileHandler.write( json.dumps( app_data ) + "\n" )
    except Exception as e:
        print( e )

errorUrls.close()
print( 'Complete' )
closeResultFiles( fileHandlers )
