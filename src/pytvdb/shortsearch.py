'''
Created on Feb 19, 2010

@author: mattdc
'''

from xml.etree import ElementTree
from pytvdb import httphelper

mirrorUrl = r'http://thetvdb.com/'
mirrorPort = '80'

searchForShortSeriesPath = 'api/GetSeries.php'

bannerURL = mirrorUrl + r'banners/'

class ShortSeriesData():
    tvdbId = ''
    name = u''
    bannerUrl = ''
    overview = []
    firstAiredDate = ''
    
    def __unicode__(self):
        output = 'name:|' + self.name + '| ' + 'tvdbid:|' + self.tvdbId + '| ' + 'bannerUrl:|' + self.bannerUrl + '| ' + 'overview:|' + self.overview + '| ' + 'firstAiredDate:|' + self.firstAiredDate + '|'
        
        return output

def xmlToShortSeries(xmlSeries):
    seriesResult = ShortSeriesData()
    
    for element in xmlSeries.getiterator():
        if element.tag == 'Overview':
            
            lines = element.text.splitlines()
            seriesResult.overview = lines
            
            continue
        
        if element.tag == 'id':
            seriesResult.tvdbId = element.text
            continue
        
        if element.tag == 'SeriesName':
            seriesResult.name = element.text
            continue
        
        if element.tag == 'banner':
            seriesResult.bannerUrl = bannerURL + element.text
            continue
        
        if element.tag == 'FirstAired':
            seriesResult.firstAiredDate = element.text
            continue
        
    return seriesResult

def searchForShortSeries(seriesName):
    params = {'seriesname':seriesName}
    response = httphelper.doGetRequest(mirrorUrl, mirrorPort, searchForShortSeriesPath, params)
    seriesXmlList = ElementTree.parse(response).findall(r'.//Series')
    
    searchResults = []
    for xmlSeries in seriesXmlList:
        result = xmlToShortSeries(xmlSeries)
        
        searchResults.append(result)
    
    return searchResults
