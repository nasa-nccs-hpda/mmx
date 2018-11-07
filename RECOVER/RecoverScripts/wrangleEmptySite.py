#!/usr/bin/python

import argparse
import datetime
import os
import sys
import time

import wranglerUtils

#-------------------------------------------------------------------------------
# checkDates
#-------------------------------------------------------------------------------
def checkDates(startDate, endDate):
    
    if startDate == None and endDate == None:
        return
        
    datetime.datetime.strptime(startDate, '%Y-%m-%d')
    datetime.datetime.strptime(endDate,   '%Y-%m-%d')
    
#-------------------------------------------------------------------------------
# createEmptySite
#-------------------------------------------------------------------------------
def createEmptySite(ulx, uly, lrx, lry, epsg, user, key, \
                    startDate = None, endDate = None,    \
                    server = 'recoverdss.us', verbose = False):
                    
    # Validate the input.
    if user == None or user == '':
        raise RuntimeError('A user must be provided.')
        
    if key == None or key == '':
        raise RuntimeError('A key must be provided.')
        
    key     = key
    server  = server
    user    = user
    verbose = verbose
    
    validate(ulx, uly, lrx, lry, epsg, verbose)
    checkDates(startDate, endDate)

    # Prepare the API arguments
    args = {'ulx'        : str(ulx),
            'uly'        : str(uly),
            'lrx'        : str(lrx),
            'lry'        : str(lry),
            'epsg'       : str(epsg),
            'siteName'   : 'WRANGLE_EMPTY_SITE-' + str(time.time()),
            'key'        : key,
            'user'       : user,
            'predictors' : []}
            
    if startDate != None:
        args['startDate'] = startDate
        
    if endDate != None:
        args['endDate'] = endDate
            
    # Invoke the API.
    response = wranglerUtils.callAPI(server, 'order', args)
    msg = response['msg']
    
    if response['success']:
        print 'Your site ID is: ' + str(msg)
        
    else:
        raise RuntimeError('Unable to create this site due to: ' + str(msg))
        
    return msg
        
#---------------------------------------------------------------------------
# validate
#---------------------------------------------------------------------------
def validate (ulx, uly, lrx, lry, epsg, verbose):
	
    if ulx != None and uly != None and lrx != None and lry != None:

    	if verbose:
    		print 'ulx: ' + str(ulx)
    		print 'uly: ' + str(uly)
    		print 'lrx: ' + str(lrx)
    		print 'lry: ' + str(lry)

    	if float(ulx) >= float(lrx):
    		raise RuntimeError('The upper-left X, ' + str(ulx) + ' must be less than the lower-right X, ' + str(lrx))

    	if float(uly) <= float(lry):
    		raise RuntimeError('The upper-left Y, ' + str(uly) + ' must be greater than the lower-right Y, ' + str(lry))
        
    else:
        raise RuntimeError('The corner coordinates must be provided.')
	
#-------------------------------------------------------------------------------
# main
# 
# ./wrangleEmptySite.py --ulx 306099.6369 --uly 4802508.3822 --lrx 352339.7992 --lry 4754696.1116 --epsg 26912 --startDate 2016-01-01 --endDate 2016-02-29
#-------------------------------------------------------------------------------
def main():

    #---
    # Process command-line args. 
    #---
    desc = 'This application creates a Wrangler site with no predictors.'

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--ulx', required = True)
    parser.add_argument('--uly', required = True)
    parser.add_argument('--lrx', required = True)
    parser.add_argument('--lry', required = True)
    parser.add_argument('--epsg', required = True, help='the integer EPSG code')
    parser.add_argument('--startDate', help='YYYY-MM-DD')
    parser.add_argument('--endDate', help='YYYY-MM-DD')
    parser.add_argument('-v', help='show verbose progress messages', action='store_true')
    args = parser.parse_args()

    # server = 'dev.nasawrangler.us'
    server = 'recoverdss.us'
    # server = 'localhost:8000'
    user   = 'ISU'
    key    = '6325b661-b111-4085-9b48-997d343f1d9a'
    # user   = 'wmAdmin'
    # key    = '13c952ea-9ca6-4248-a6b1-f9af29a1fa37'

    createEmptySite(args.ulx, args.uly, args.lrx, args.lry, args.epsg, \
                    user, key, args.startDate, args.endDate, server, args.v)
    
#-------------------------------------------------------------------------------
# Invoke the main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
        
