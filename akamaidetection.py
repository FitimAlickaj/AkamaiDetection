from turtle import down
from numpy import ma
import vlc
import time
import requests
import json
import sys
import cv2
import gspread
from oauth2client import service_account
from oauth2client.service_account import ServiceAccountCredentials
from streamList import akamaiSources
import logging
import threading
# #Sheets Config
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
akamai = client.open("Tier1 Bot Data").worksheet("API-CHANNEL-LIST")
#Slack Config
slack_token = 'xoxb-302006564691-1725170443333-g2jjIG1VvlPrUYrX2EG4dT80'
slack_channel = '#system-monitoring'
slack_icon_emoji = ':eyes:'
slack_user_name = 'SUPPORT' # name of app in slack
akamaiStreams = akamaiSources
def post_message_to_slack(text, blocks=None):
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_token,
        'channel': slack_channel,
        'text': text,
        'icon_emoji': slack_icon_emoji,
        'username': slack_user_name,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()
downList = []
downAudio = []
cv2Detection = []

logging.basicConfig(filename='akamai.log', filemode='a+', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def detection(source):
	firstFilter = source[:source.find('.m3u8')].strip()
	main = firstFilter[:firstFilter.find('main')].strip()
	main = main.replace('http://setp-eu-glb-mslv4.akamaized.net/hls/live/','')
	logging.warning("Channel in Detection: " + main)
	try:
		video = cv2.VideoCapture(str(source))
		fps = video.get(cv2.CAP_PROP_FPS)
		if fps < 24:
			logging.error("Channel Error")
			if main in cv2Detection:
				pass
				video.release()
			else:
				post_message_to_slack(main + "\n" + "Source issue")
				cv2Detection.append(main)
				video.release()
		else:
			if main in cv2Detection:
				cv2Detection.remove(main)
				post_message_to_slack(main + "\n" + "Source back to normal")
			logging.warning("Channel Passed OPENCV DETECTION")
			video.release()
			media_player = vlc.MediaPlayer()
			media = vlc.Media(source)
			media_player.set_media(media)
			media_player.play()
			time.sleep(5)
			value = media_player.is_playing()
			if value == 1:
				timevideo = media_player.get_time()
				audio = media_player.audio_get_channel()
				mediaMuted = media_player.audio_get_mute()
				speed = media_player.get_rate()
				logging.warning("Channel Speed: " + str(speed)) 
				logging.warning("Source Playing: " + str(main))
				logging.warning("SourceAudio is: " + str(audio) + " " + "FramesPlaying " + str(timevideo) + " Muted " + str(mediaMuted))
				if timevideo < 5000:
					logging.error("Repeated Scene")
					if main in downList:
						pass
					else:
						post_message_to_slack(main + " Source issue")
						downList.append(main)
				else:
					if main in downList:
						downList.remove(main)
						logging.warning("Repeated Scene Fixed")
						post_message_to_slack(main + " Source back to normal")
					if audio == 0:
						logging.error("No Audio")
						if main in downAudio:
							pass
						else:
							post_message_to_slack(main + " Source has no audio")
							downAudio.append(main)
					else:
						if main in downAudio:
							downAudio.remove(main)
							logging.warning("Audio Fixed")
							post_message_to_slack(main + " Audio of source has been fixed")
					if audio == 0:
						logging.error("No Audio")
						if main in downAudio:
							pass
						else:
							post_message_to_slack(main + " Source has no audio")
							downAudio.append(main)
					else:
						if main in downAudio:
							downAudio.remove(main)
							logging.warning("Audio Fixed")
							post_message_to_slack(main + " Audio of source has been fixed")
					media_player.stop()
	except cv2.error as e:
		post_message_to_slack("Source Error " + main)
		cv2Detection.append(main)
		logging.error("Error OPENCV " + main)



def mainChannels():
	for i in range(5):
		detection("http://setp-eu-glb-mslv4.akamaized.net/hls/live/2010312/tringshqip/main.m3u8?hdnts=exp=1642969692~acl=/*~hmac=27ab505a20a6c862fbe334460bbf4c347e49e369e44b044511d5f940e5d428da")
def tringChannels():
	for i in range(3):	
		detection("http://setp-eu-glb-mslv4.akamaized.net/hls/live/2008362/tringtring/main.m3u8?hdnts=exp=1642969697~acl=/*~hmac=c5bd2ef9c0215cf21273aa1c494fee054fbe1b09da0b6d5e314a67f0f8ba5767")
def digitalbChannels():
	for i in range(2):
		detection("http://setp-eu-glb-mslv4.akamaized.net/hls/live/2008362/tringkids/main.m3u8?hdnts=exp=1642969703~acl=/*~hmac=24805a9b4a44e97864471fdd4c2129ccff30d83336859292cdefd8cd0d89a098")


threading.Thread(target=mainChannels).start()
threading.Thread(target=tringChannels).start()
threading.Thread(target=digitalbChannels).start()



