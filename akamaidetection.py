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
			if source in cv2Detection:
				pass
				video.release()
			else:
				post_message_to_slack(main + "\n" + "OpenCV Detection lowen than 24 fps")
				cv2Detection.append(source)
				video.release()
		else:
			if source in cv2Detection:
				cv2Detection.remove(source)
				post_message_to_slack(main + "\n" + "OpenCV Detection FPS Fixed")
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
					if source in downList:
						pass
					else:
						post_message_to_slack(main + " Source Repeating same scene")
						downList.append(source)
				else:
					if source in downList:
						downList.remove(source)
						logging.warning("Repeated Scene Fixed")
						post_message_to_slack(main + " Source Repeating same scene is back to normal")
					if audio == 0:
						logging.error("No Audio")
						if source in downAudio:
							pass
						else:
							post_message_to_slack(main + " Source has no audio")
							downAudio.append(source)
					else:
						if source in downAudio:
							downAudio.remove(source)
							logging.warning("Audio Fixed")
							post_message_to_slack(main + " Audio of source has been fixed")
					if audio == 0:
						logging.error("No Audio")
						if source in downAudio:
							pass
						else:
							post_message_to_slack(main + " Source has no audio")
							downAudio.append(source)
					else:
						if source in downAudio:
							downAudio.remove(source)
							logging.warning("Audio Fixed")
							post_message_to_slack(main + " Audio of source has been fixed")
					media_player.stop()
	except cv2.error as e:
		post_message_to_slack("Source Error " + main)
		cv2Detection.append(source)
		logging.error("Error OPENCV " + main)


def mainChannels():
	for i in range(5):
		detection("")


def tringChannels():
	for i in range(3):	
		detection("")


def digitalbChannels():
	for i in range(2):
		detection("")




threading.Thread(target=mainChannels).start()
threading.Thread(target=tringChannels).start()
threading.Thread(target=digitalbChannels).start()



