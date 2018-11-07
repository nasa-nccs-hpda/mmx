
import json
import ssl
import urllib
import urllib2

#---------------------------------------------------------------------------
# callAPI
#---------------------------------------------------------------------------
def callAPI(endPoint, command, args, verbose = False):

    orderURL = composeURL(endPoint, command, args)
    
    if verbose:
        print orderURL
        
    response = sendRequest(orderURL)

    return response

#---------------------------------------------------------------------------
# composeURL
#---------------------------------------------------------------------------
def composeURL(endPoint, command, args):

    httpPrefix = 'https://'
    
    if endPoint[:8] != httpPrefix:
        endPoint = httpPrefix + endPoint
    
    endPoint += '/api/'
    orderURL  = endPoint + command + '?' + urllib.urlencode(args)

    return orderURL
    
#-------------------------------------------------------------------------------
# openURL
#-------------------------------------------------------------------------------
def openURL(sendURL):
    
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        response = urllib2.urlopen(sendURL, context = ctx)
        return response
    
#-------------------------------------------------------------------------------
# sendRequest
#-------------------------------------------------------------------------------
def sendRequest(sendURL):

    doc = {}

    try:

        # Send request, then parse the response.
        # ctx = ssl.create_default_context()
        # ctx.check_hostname = False
        # ctx.verify_mode = ssl.CERT_NONE
        #
        # doc = json.loads(urllib2.urlopen(sendURL, context = ctx).readline())
        doc = json.loads(openURL(sendURL).readline())
            
    except urllib2.HTTPError, e:
    
        doc['msg']     = 'HTTP error: %d' % e.code + '\n'
        doc['state']   = 'FAILED'
        doc['success'] = False
        
    except urllib2.URLError, e:
    
        doc['msg']     = 'Network error: %s' % e.reason + '\n'
        doc['state']   = 'FAILED'
        doc['success'] = False
        
    except Exception, e:
    
        doc['msg']     = e
        doc['state']   = 'FAILED'
        doc['success'] = False
    
    return doc
