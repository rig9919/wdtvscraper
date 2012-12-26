'''
Created on Feb 20, 2010

@author: mattdc
'''

import urllib
import urllib2

def doGetRequest(serverUrl, serverPort, serverPath, paramsDict):
    encodedParams = urllib.urlencode(paramsDict)
    fullPath = serverUrl + serverPath + '?' + encodedParams
    
    request = urllib2.Request(fullPath)
    response = urllib2.urlopen(request)
    
    return response