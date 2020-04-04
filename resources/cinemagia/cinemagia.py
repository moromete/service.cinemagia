import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pytz import timezone
import xml.etree.ElementTree as ET
import re

class Cinemagia():
  url = 'https://www.cinemagia.ro/program-tv/'

  headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'identity',
    'Accept-Language': 'en-US,en;q=0.5', 
    'Connection': 'keep-alive',
    'Host': 'www.cinemagia.ro',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
  }

  debug = True
  filePath = 'tvxml.xml'

  def __init__( self , *args, **kwargs):
    if(kwargs.get('filePath')):
      self.filePath=kwargs.get('filePath')

  def execute(self):

    tv = ET.Element('tv')
    tv.set('source-info-url', self.url)
    tv.set('source-info-name', 'cinemagia')

    request = urllib.request.Request(self.url, None, self.headers)
    with urllib.request.urlopen(request) as response:
      html = response.read()

    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all('div', class_="col")
    for item in items:
      catNodes = item.findChildren("h2")
      chContainerNodes = item.findChildren("ul")
      i = 0
      for catNode in catNodes:
        #print(catNode)
        catName = catNode.string.split('-')[1].strip().lower()
        if((catName != 'canale hd') and (catName != 'erotice')):
          print(catName)
          # print(chContainerNodes[i])
          chNodes = chContainerNodes[i].findChildren('a', class_="station-link", href=True)
          for chNode in chNodes:
            channelName = chNode.string
            print(channelName)
            channel = ET.SubElement(tv, 'channel')
            channel.set('id', channelName)
            displayName = ET.SubElement(channel, 'display-name')
            displayName.text = channelName
            self.scrapEpg(chNode['href'], tv, channelName)

            if(self.debug):
              break
        i = i + 1
        if(self.debug):
          break
      if(self.debug):
        break
    
    tree = ET.ElementTree(tv)
    tree.write(self.filePath, encoding='utf-8', xml_declaration=True)

  def scrapEpg(self, url, tv, channelName):
    #print(url)
    request = urllib.request.Request(url, None, self.headers)
    with urllib.request.urlopen(request) as response:
      html = response.read()
    # print(html)

    currentDate = datetime.now(timezone('Europe/Bucharest'))
    
    arrIds = ['showContainer-OLD', 'showContainer-NEXT', 'showContainer-MORNING', 'showContainer-EVENING']
    for idNode in arrIds:
      soup = BeautifulSoup(html, "html.parser")
      contNode = soup.find('tr', id=idNode)
      if(contNode):
        contEvents = contNode.findChild(class_='container_events')
        # print(contEvents)
        oraNodes = contEvents.findChildren('td', class_='ora')
        eventNodes = contEvents.findChildren('td', class_='event')
        
        i=0
        for oraNode in oraNodes:
          ora = oraNode.contents[1].string
          #print(ora)
          titleNode = eventNodes[i].findChild(class_='title')
          titleLinkNode = titleNode.findChild('a', title=True, href=True)
          if(titleLinkNode):
            title = titleLinkNode['title']
          else:
            title = titleNode.contents[0]
          title = title.strip()
          #print(title)
          
          #start datetime
          arrOra = ora.split(':')
          h = int(arrOra[0])
          m = int(arrOra[1])
          startDateTime = currentDate.replace(hour=h, minute=m, second=0, microsecond=0)
          # next day
          if(h < 7):
            startDateTime += timedelta(days=1)
          #print(startDateTime)

          #stop datetime
          if((i+1) < len(oraNodes)):
            ora = oraNodes[i+1].contents[1].string
            arrOra = ora.split(':')
            h = int(arrOra[0])
            m = int(arrOra[1])
            stopDateTime = currentDate.replace(hour=h, minute=m, second=0, microsecond=0)
            # next day
            if(h < 7):
              stopDateTime += timedelta(days=1)
          else:
            stopDateTime = currentDate.replace(hour=7, minute=0, second=0, microsecond=0)
            stopDateTime += timedelta(days=1)
          #print(stopDateTime)

          programmeElm = ET.SubElement(tv, 'programme')
          programmeElm.set('start', startDateTime.strftime("%Y%m%d%H%M%S %z"))
          programmeElm.set('stop', stopDateTime.strftime("%Y%m%d%H%M%S %z"))
          programmeElm.set('channel', channelName)
          titleElm = ET.SubElement(programmeElm, 'title')
          titleElm.text = title
          dateElm = ET.SubElement(programmeElm, 'date')
          dateElm.text = startDateTime.strftime("%Y%m%d")

          #event details
          if(titleLinkNode):
            self.getEventDetails(titleLinkNode['href'], programmeElm)

          i=i+1

  def getEventDetails(self, url, programmeElm):
    # print(url)
    request = urllib.request.Request(url, None, self.headers)
    with urllib.request.urlopen(request) as response:
      html = response.read()

    soup = BeautifulSoup(html, "html.parser")

    descAll = ''

    genNode = soup.find('div', id='movieGenreUserChoiceResults')
    if(genNode):
      gen = genNode.text.strip()
      p = re.compile('[\n]+')
      gen = p.sub(", ", gen)
      descAll += gen

    ratingNode = soup.find('div', class_='imdb-rating')
    if(ratingNode):
      rating = ratingNode.text.strip()
      descAll += "\n" + rating
    
    descNode = soup.find('div', id='short_body_sinopsis')
    if(descNode):
      desc= descNode.text.strip()
      descAll += "\n" + desc
    
    # print(descAll)

    descElm = ET.SubElement(programmeElm, 'desc')
    descElm.text = descAll
    descElm.set('lang', 'ro')
   