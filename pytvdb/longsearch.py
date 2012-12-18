'''
Created on Feb 19, 2010

@author: mattdc
'''

from pytvdb import settings, httphelper, shortsearch, unziphelper
from xml.etree import ElementTree
import os.path
import tempfile
import shutil
import re

sizeRegex = re.compile(r'(\d{1,5})x(\d{1,5})')

searchForFullSeriesUrlPrefix = r'/api/' + settings.apikey + r'/series/'
searchForFullSeriesUrlSuffix = r'/all/en.zip'

mirrorUrl = r'http://www.thetvdb.com/'
mirrorPort = '80'

serverTimePath = r'api/Updates.php'
serverTimeParams = {'type':'none'}

bannerURL = mirrorUrl + r'banners/'

class BannerData():
    url = ''
    thumbUrl = ''
    type = ''
    width = ''
    height = ''

class ActorData():
    name = ''
    role = ''
    imageUrl = ''

class EpisodeData():
    tvdbId = ''
    name = ''
    overview = ''
    episodeNumber = ''
    seasonNumber = ''   
    language = ''
    firstAired = ''   
    director = []
    writer = []
    guestStars = []   
    bannerUrl = ''


class LongSeriesData(shortsearch.ShortSeriesData):
    episodes = []
    actors = []
    genres = []
    status = ''
    contentRating = ''
    airsDayOfWeek = ''
    airsTime = ''
    language = ''
    network = ''  
    banners = []
    fanartUrl = ''
    posterUrl = ''  
    imdbId = []
    zap2itId = ''
    updatedTime = ''

def buildFullSeriesURL(tvdbId):
    output = searchForFullSeriesUrlPrefix + tvdbId + searchForFullSeriesUrlSuffix
    return output

def XMLToEpisodes(episodeList):
    output = []
    
    for episodeElement in episodeList:
        episode = EpisodeData()
        for element in episodeElement.getiterator():
            
            if element.tag == 'id':
                episode.tvdbId = element.text
                continue
            
            if element.tag == 'EpisodeName':
                episode.name = element.text
                continue
            
            if element.tag == 'Overview':
                if element.text == None:
                    continue
                episode.overview = element.text.splitlines()
                continue
            
            if element.tag == 'EpisodeNumber':
                episode.episodeNumber = element.text
                continue
            
            if element.tag == 'SeasonNumber':
                episode.seasonNumber = element.text
                continue
            
            if element.tag == 'Language':
                episode.language = element.text
                continue
            
            if element.tag == 'FirstAired':
                episode.firstAired = element.text
                continue
            
            if element.tag == 'Director':
                text = element.text
                if not text:
                    continue              
                episode.director = text.strip('|').split('|')
                continue
            
            if element.tag == 'Writer':              
                text = element.text
                if not text:
                    continue
                episode.writer = text.strip('|').split('|')
                continue
            
            if element.tag == 'GuestStars':
                text = element.text
                if not text:
                    continue
                episode.guestStars = text.strip('|').split('|')
                continue
            
            if element.tag == 'filename':
                if not element.text:
                    continue
                episode.bannerUrl = bannerURL + element.text
                continue
        
        output.append(episode)
    
    return output

def XMLToLongSeries(seriesXMLFile):
    output = LongSeriesData()
    
    docRoot = ElementTree.parse(seriesXMLFile)
    seriesElement = docRoot.find(r'.//Series')
    
    for element in seriesElement.getiterator():
        if element.tag == 'id':
            output.tvdbId = element.text
            continue
        
        if element.tag == 'Overview':
            output.overview = element.text.splitlines()
            continue
            
        if element.tag == 'Airs_DayOfWeek':
            output.airsDayOfWeek = element.text
            continue
        
        if element.tag == 'Airs_Time':
            output.airsTime = element.text
            continue
        
        if element.tag == 'ContentRating':
            output.contentRating = element.text
            continue
            
        if element.tag == 'FirstAired':
            output.firstAiredDate = element.text
            continue
            
        if element.tag == 'Genre':
            text = element.text
            if not text:
                continue            
            output.genres = text.strip('|').split('|')
            continue
            
        if element.tag == 'IMDB_ID':
            output.imdbId = element.text
            continue
            
        if element.tag == 'Language':
            output.language = element.text
            continue
            
        if element.tag == 'Network':
            output.network = element.text
            continue
            
        if element.tag == 'SeriesName':
            output.name = element.text
            continue
        
        if element.tag == 'Status':
            output.status = element.text
            continue
        
        if element.tag == 'banner':
            if not element.text:
                continue
            
            output.bannerUrl = bannerURL + element.text
            continue
        
        if element.tag == 'fanart':
            if not element.text:
                continue
            
            output.fanartUrl = bannerURL + element.text
            continue
            
        if element.tag == 'poster':
            if not element.text:
                continue
            
            output.posterUrl = bannerURL + element.text
            continue
            
        if element.tag == 'zap2it_id':
            output.zap2itId = element.text
            continue
        
    episodeList = docRoot.findall(".//Episode")
    output.episodes = XMLToEpisodes(episodeList)
    return output

def XMLToActors(actorsXMLFile):
    output = []
    
    actorElements = ElementTree.parse(actorsXMLFile).findall(r'.//Actor')
    for actorElement in actorElements:
        actor = ActorData()
        for element in actorElement.getiterator():
            if element.tag == 'Name':
                actor.name = element.text
                continue
            
            if element.tag == 'Role':
                actor.role = element.text
                continue
            
            if element.tag == 'Image':
                if not element.text:
                    continue
                
                actor.imageUrl = bannerURL + element.text
                continue
        
        output.append(actor)
    
    
    return output

def XMLToBanners(bannersXMLFile):
    output = []
    
    bannerElements = ElementTree.parse(bannersXMLFile).findall(r'.//Banner')
    for bannerElement in bannerElements:
        banner = BannerData()
        
        for element in bannerElement.getiterator():
            if element.tag == 'BannerPath':
                banner.url = bannerURL + element.text
                continue
            
            if element.tag == 'BannerType':
                banner.type = element.text
                continue
            
            if element.tag == 'ThumbnailPath':
                banner.thumbUrl = bannerURL + element.text
                continue
            
            if element.tag == 'BannerType2':
                match = sizeRegex.match(element.text)
                if not match:
                    continue               
                banner.width = match.group(1)
                banner.height = match.group(2)
                continue

        output.append(banner)
    return output

def getServerTime():
    response = httphelper.doGetRequest(mirrorUrl, mirrorPort, serverTimePath, serverTimeParams)
    timeElement = ElementTree.parse(response).findall(r'.//Time')

    timeSinceEpoch = timeElement[0].text
    return timeSinceEpoch

def searchForLongSeries(tvdbId):
    path = buildFullSeriesURL(tvdbId)
    params = {}
    response = httphelper.doGetRequest(mirrorUrl, mirrorPort, path, params)
    
    zipFile = tempfile.NamedTemporaryFile(suffix='.zip', prefix='pytvdb', delete=True)
    zipFile.write(response.read())
    zipFile.seek(0)
    
    unZipDir = tempfile.mkdtemp()
    unZipper = unziphelper.unzip()
    unZipper.extract(zipFile, unZipDir)
    
    seriesXML = os.path.join(unZipDir, 'en.xml')
    if os.path.isfile(seriesXML):
        seriesXMLFile = open(seriesXML)
        series = XMLToLongSeries(seriesXMLFile)
        seriesXMLFile.close()
    
    actorsXML = os.path.join(unZipDir, 'actors.xml')
    if os.path.isfile(actorsXML):
        actorsXMLFile = open(actorsXML)
        series.actors = XMLToActors(actorsXMLFile)
        actorsXMLFile.close()
        
    bannersXML = os.path.join(unZipDir, 'banners.xml')
    if os.path.isfile(bannersXML):
        bannersXMLFile = open(bannersXML)
        series.banners = XMLToBanners(bannersXMLFile)
        bannersXMLFile.close()
    
    series.updatedTime = getServerTime()
    
    zipFile.close()
    shutil.rmtree(unZipDir)
    
    
    return series
