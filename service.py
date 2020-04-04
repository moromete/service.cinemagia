import xbmc, xbmcaddon
import os
from resources.cinemagia.cinemagia import Cinemagia
import time

addon = xbmcaddon.Addon('service.cinemagia')
PROFILE = xbmc.translatePath(addon.getAddonInfo('profile'))
TVXML_FILE = 'tvxml.xml'
filePath = os.path.join(PROFILE, TVXML_FILE)

fileTime = os.path.getmtime(filePath)
currentTime = time.time()

if(currentTime - fileTime > (3600 * 12)): #older than 12hours
  cm = Cinemagia(filePath = filePath)
  cm.debug = True
  cm.execute()  


