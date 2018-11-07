#!/usr/bin/python

import argparse
import os
import sys
import time
import urllib2

import wranglerUtils

#---------------------------------------------------------------------------
# wrangle
#---------------------------------------------------------------------------
def wrangle(user, key, site, gpcp, landsat, merra, merraMax, modis, \
            server = 'recoverdss.us', verbose = False):
    
    if user == None or user == '':
        raise RuntimeError('A user must be provided.')
        
    if key == None or key == '':
        raise RuntimeError('A key must be provided.')

    predictor = None

    if gpcp:
        predictor = 'GPCP'
        
    elif landsat:
        predictor = 'Landsat'
        
    elif merra:
        predictor = 'MERRA'
        
    elif merraMax:
        predictor = 'MERRA Max'
        
    elif modis:
        predictor = 'MODIS Time Series'
        
    # Initiate the predictor.
    args = {'site'          : site,
            'key'           : key,
            'user'          : user,
            'predictorName' : predictor}
    
    predCreated = False
    
    while not predCreated:
        
        response = wranglerUtils.callAPI(server, 'addPredictor', args, verbose)

        if not response['success']:

            if response.has_key('state') and response['state'] == 'FLD' and \
               response.has_key('message') and 'failed' in response['message']:
            
                #---
                # This happens when: 1) the site does not exist, 2) the end
                # point / predictor does not exist, 3) the predictor processing
                # failed.  For case 3, it is worth re-trying.  To identify
                # case 3, look for 'failed' in the message.
                #---
                delResp = wranglerUtils.callAPI(server, 'deletePredictor', args)
            
            else:
                print 'Unable to add this predictor due to: ' + str(response['msg'])
                return
                
        else:
            predCreated = True

        print response['msg']
    
    # Wait for it to complete.
    startTime = time.time()
    
    # 60 secs * 60 mins * 24 hours * 2 = 2 days
    maxWait = 60 * 60 * 24 * 2 
    
    status    = None
    firstTime = True
    
    while status != 'CPT' and status != 'FLD':
        
        if not firstTime: 
            
            # Wait
            print 'Waiting ...'
            time.sleep(5)
            waited = time.time() - startTime

            if waited > maxWait and status != 'CPT':

                print 'Job has not completed in ' + str(maxWait) + ' seconds, so timing out.'
                return

        else:
            firstTime = False
            
        # Check the status
        response = wranglerUtils.callAPI(server, 'predictorStatus', args, verbose)
        status   = response['state']
        msg      = response['msg']

    if status == 'FLD':
        
        print 'Predictor creation failed.'
        print msg
        return

    # Download it.
    print 'Downloading ' + predictor
    
    args = {'site'      : site,
            'predictor' : predictor,
            'key'       : key,
            'user'      : user}
    
    downloadURL  = wranglerUtils.composeURL(server, 'downloadPredictor', args) 

    # downloadFile = urllib2.urlopen(downloadURL)
    downloadFile = wranglerUtils.openURL(downloadURL)
    
    outFileName  = os.path.join(os.getcwd(), predictor + '.zip')

    oFile = open(outFileName, 'wb')
    oFile.write(downloadFile.read())
    downloadFile.close()
    oFile.close()

    print 'Predictor file: ' + str(outFileName)
    return outFileName
    
#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
def main():

    #---
    # Process command-line args. 
    #---
    desc = 'This application adds MERRA to a site, creating the site, if necessary.'

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-s', required = True, help='site ID')
    parser.add_argument('-v', help='show verbose progress messages', action='store_true')

    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument('--gpcp',      action='store_true')
    group.add_argument('--landsat',   action='store_true')
    group.add_argument('--merra',     action='store_true')
    group.add_argument('--merra_max', action='store_true')
    group.add_argument('--modis',     action='store_true')

    args = parser.parse_args()

    # server = 'dev.nasawrangler.us'
    server = 'recoverdss.us'
    # server = 'localhost:8000'
    user   = 'ISU'
    key    = '6325b661-b111-4085-9b48-997d343f1d9a'
    # user   = 'wmAdmin'
    # key    = '13c952ea-9ca6-4248-a6b1-f9af29a1fa37'

    wrangle(user, key, args.s, args.gpcp, args.landsat, args.merra, \
            args.merra_max, args.modis, server, args.v)
    
#-------------------------------------------------------------------------------
# Invoke the main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
        sys.exit(main())
        
