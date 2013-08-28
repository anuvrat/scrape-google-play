'''
Created on Aug 28, 2013

@author: anuvrat
'''

from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import codecs

character_encoding = 'utf-8'

def getAppsData( category, start, num, app_type ):
    url = 'https://play.google.com/store/apps/category/' + category + '/collection/topselling_' + app_type
    values = {'start' : start,
              'num': num,
              'numChildren':'0',
              'ipf': '1',
              'xhr': '1'}
    data = urllib.parse.urlencode( values )
    data = data.encode( character_encoding )
    req = urllib.request.Request( url, data )
    try:
        response = urllib.request.urlopen( req )
    except urllib.error.HTTPError:
        print( "HTTPError with: ", url )
        return []
    the_page = response.read()

    apps = []
    soup = BeautifulSoup( the_page )
    for div in soup.findAll( 'div', {'class' : 'details'} ):
        title = div.find( 'a', {'class':'title'} )
        subtitle = div.find( 'a', {'class' : 'subtitle'} )
        apps.append( [title.get_text().strip(), subtitle.get_text().strip(), title.get( 'href' ), subtitle.get( 'href' )] )

    return apps

categories = ['BOOKS_AND_REFERENCE', 'BUSINESS', 'COMICS', 'COMMUNICATION', 'EDUCATION', 'ENTERTAINMENT', 'FINANCE', 'HEALTH_AND_FITNESS', 'LIBRARIES_AND_DEMO', 'LIFESTYLE', 'APP_WALLPAPER', 'MEDIA_AND_VIDEO', 'MEDICAL', 'MUSIC_AND_AUDIO', 'NEWS_AND_MAGAZINES', 'PERSONALIZATION', 'PHOTOGRAPHY', 'PRODUCTIVITY', 'SHOPPING', 'SOCIAL', 'SPORTS', 'TOOLS', 'TRANSPORTATION', 'TRAVEL_AND_LOCAL', 'WEATHER', 'ARCADE', 'BRAIN', 'CARDS', 'CASUAL', 'GAME_WALLPAPER', 'RACING', 'SPORTS_GAMES', 'GAME_WIDGETS']
app_types = ['free', 'paid']

for category, app_type in [( x, y ) for x in categories for y in app_types]:
    print( "Type = ", app_type, " Cateory = ", category )

    resultFile = codecs.open( '_'.join( ["apps", category.lower(), app_type.lower()] ), 'wb', character_encoding )

    previous_apps = []
    start_idx = 0
    size = 100
    apps_count = 0
    while(True):
        apps = getAppsData( category, start_idx, size, app_type )
        if apps == previous_apps: break
        for app in apps:
            try:
                resultFile.write( '\t'.join( app ) + "\n" )
            except Exception as e:
                print( e )
        previous_apps = apps
        start_idx += size
        apps_count += len( apps )
        print( apps_count )

    print( 'Done', apps_count )
    resultFile.close()

print('Complete')
