from turtle import down
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
logging.basicConfig(filename='akamai.log', filemode='a+', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
def vlcCheck(source):
	media_player = vlc.MediaPlayer()
	media = vlc.Media(source)
	media_player.set_media(media)
	media_player.play()
	time.sleep(4)
	value = media_player.is_playing()
	if value == 1:
		timevideo = media_player.get_time()
		audio = media_player.audio_get_channel()
		mediaMuted = media_player.audio_get_mute()
		speed = media_player.get_rate()
		logging.warning("Speed of channel " + str(speed))
		logging.warning("Source Playing " + source)
		logging.warning("SourceAudio is " + str(audio) + " " + "Frames playing " + str(timevideo) + " Muted " + str(mediaMuted))
		if timevideo < 5000:
			logging.error("Repeated Scene")
			if source in downList:
				pass
			else:
				post_message_to_slack(source + " Source Repeating same scene")
				downList.append(source)
		else:
			if source in downList:
				downList.remove(source)
				logging.warning("Repeated Scene Fixed")
				post_message_to_slack(source + " Source Repeating same scene is back to normal")
			if audio == 0:
				logging.error("No Audio")
				if source in downAudio:
					pass
				else:
					post_message_to_slack(source + " Source has no audio")
					downAudio.append(source)
			else:
				if source in downAudio:
					downAudio.remove(source)
					logging.warning("Audio Fixed")
					post_message_to_slack(source + " Audio of source has been fixed")
			if audio == 0:
				logging.error("No Audio")
				if source in downAudio:
					pass
				else:
					post_message_to_slack(source + " Source has no audio")
					downAudio.append(source)
			else:
				if source in downAudio:
					downAudio.remove(source)
					logging.warning("Audio Fixed")
					post_message_to_slack(source + " Audio of source has been fixed")
			media_player.stop()
def detection(source):
	video = cv2.VideoCapture(str(source))
	fps = video.get(cv2.CAP_PROP_FPS)
	if fps < 24:
		logging.error("Source Lowen than 24 " + source)
		if source in cv2Detection:
			pass
			video.release()
		else:
			post_message_to_slack(source + "\n" + "OpenCV Detection lowen than 24 fps")
			cv2Detection.append(source)
			video.release()
	else:
		if source in cv2Detection:
			cv2Detection.remove(source)
			post_message_to_slack(source + "\n" + "OpenCV Detection FPS Fixed")
		video.release()
		vlcCheck(source)


akamaiStreams = akamai.col_values(4)
def run():
	for stream in akamaiStreams:
		logging.warning("New Channel in detection")
		detection(stream)


run()