import xbmc, xbmcgui, xbmcaddon
import os
from resources.cinemagia.cinemagia import Cinemagia
import time

addon = xbmcaddon.Addon('service.cinemagia')
PROFILE = xbmc.translatePath(addon.getAddonInfo('profile'))
if(not os.path.isdir(PROFILE)):
  os.mkdir(PROFILE)  
TVXML_FILE = 'tvxml.xml'
filePath = os.path.join(PROFILE, TVXML_FILE)

fileTime = None
if (os.path.isfile(filePath)):
  fileTime = os.path.getmtime(filePath)
currentTime = time.time()

if(fileTime == None or currentTime - fileTime > (3600 * 12)): #older than 12hours
  cm = Cinemagia(filePath = filePath)
  # cm.debug = True
  pDialog = xbmcgui.DialogProgressBG()
  pDialog.create(addon.getLocalizedString(30000), addon.getLocalizedString(30001))
  time.sleep(1)
  cm.execute(dlg = pDialog)
  


