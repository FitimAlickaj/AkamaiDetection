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
akamai = client.open("SheetName").worksheet("Your file name")
#Slack Config
slack_token = 'xoxb'
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


