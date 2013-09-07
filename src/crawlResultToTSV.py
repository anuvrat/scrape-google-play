'''
Created on Sep 3, 2013

@author: anuvrat
'''

import os
import json

def getAllDataaFiles():
    return ( f for f in os.listdir( path = '.' ) if os.path.isfile( f ) and f.startswith( 'apps_' ) )

def convertJsonDataIntoTSV( jsonData ):
    '''
    The csv file format is:
        app_url,title,developer,developer_link,rating,reviewers,date_published,operating_system,
        content_rating,category,email,badge,dev_website,min_downloads,max_downloads,price,currency
    '''
    data = []
    for key in ['app_url', 'title', 'developer', 'developer_link', 'rating', 'reviewers', 'date_published', 'operating_system', 'content_rating', 'category', 'email', 'badge']:
        data.append( str( jsonData[key] ).strip() if key in jsonData else 'DataNotAvailable' )

    data.append( jsonData['dev_website'][29:] if 'dev_website' in jsonData else 'DataNotAvailable' )

    for downloads in jsonData['downloads'].split( '-' ):
        data.append( downloads.strip().replace( ',', '' ) )

    data.append( str( 0 ) if jsonData['price'] == 'Free' else str( jsonData['price'] ).strip( 'Rs. ' ).strip().replace( ',', '' ) )
    data.append( 'Rs.' )
    return "\t".join( data )

if __name__ == '__main__':
    for dataFile in getAllDataaFiles():
        print( 'Processing: ', dataFile )
        fh = open( dataFile, mode = 'r', encoding = 'utf-8' )
        csvLines = [convertJsonDataIntoTSV( json.loads( line ) ) for line in fh.readlines()]
        fh.close()

        fh = open( 'data_' + dataFile + '.tsv', mode = 'w', encoding = 'utf-8' )
        fh.write( "\n".join( csvLines ) )
        fh.close()
