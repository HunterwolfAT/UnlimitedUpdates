# This script crawls given youtube channels for its 40 most recent videos,
# compares them to already known videos and adds new videos as wordpress posts to the blog 
#
# Written by Lena Siess, 2017


from oauth2client.tools import argparser
import os
import sys, traceback
import time
import json
import datetime
import parser
import getyoutubevideos
import wordpress

WAIT_TIME = 600
CHANNELS_FILENAME = "channels.json"
LOG_FILENAME = "UAlogfile.txt"
KNOWNVIDEOS_FILENAME = "knownvideos.json"

# Initialize
if os.path.isfile(CHANNELS_FILENAME) == False:
    print ("No channels.json file found!")
    quit()

if os.path.isfile(LOG_FILENAME) == False:
    print ("No logfile found! Creating it now at UAlogfile.txt")
    log_file = open(LOG_FILENAME, "a")
    log_file.write("Unlimited Ammo YouTube Script Server Log - Started " + str(datetime.datetime.now()) + "\n")
    log_file.close()

channels_file = open(CHANNELS_FILENAME).read()
channels = json.loads(channels_file)
first_run = False
added_videos = 0

knownvideos = []
set(knownvideos)

site_libraries = []

if os.path.isfile(KNOWNVIDEOS_FILENAME) == True:
    knownvideos_file_read = open(KNOWNVIDEOS_FILENAME).read()
    knownvideos = json.loads(knownvideos_file_read)

# Register with the Youtube Data API
args = argparser.parse_args()
service = getyoutubevideos.get_authenticated_service(args)

# TODO maybe have a better way to check if post already exists to avoid double posting
# So, the way its done now, is to grab the 10 newest posts, and check aginst those
# To check against ALL posts, wed have to iterate on the pages

def handle_video(channel, videoresponse, known_channel):
    global site_libraries
    global added_videos
    # Check for differences with known videos
    for playlist_item in videoresponse["items"]:
        # check if video is public and wether we already know it: returns 1 if videos exists, 0 if it doesnt:
        if playlist_item["status"]["privacyStatus"] == "public" and known_channel.count(playlist_item["snippet"]["resourceId"]["videoId"]) == 0:
            # video is not known to us yet

            # make a post about it
            # Login with the user who'se channel it is the video belongs to
            wp = wordpress.login(channel['user'],channel['password'])

            # Embed the video into the post
            post_content = playlist_item["snippet"]["description"]

            # Search the tags of the video to categorize it
            tags = getyoutubevideos.catchVideoTags(service, playlist_item["snippet"]["resourceId"]["videoId"])
            
            category = []
            for tag in tags:
                tag = tag.lower()
                if tag == "uagames" or tag == "games" or tag == "gaming" or tag == "videospiele" or tag == "video games":
                    category.append('Videospiele')
                if tag == "uaanime" or tag == "anime":
                    category.append('Anime')
                if tag == "uamanga" or tag == "manga":
                    category.append('Manga')
                if tag == "uafilm" or tag == "movies" or tag == "film":
                    category.append('Filme')
                if tag == "uaserie" or tag == "serie" or tag == "tv":
                    category.append('Serien')
            if category == []: category.append('Sonstiges')

            tags = [str(channel['name'])]
            tags.extend(category)
            category.append('Videos')
            
            #print str(tags) + "|" + str(category) + " >> " + str(channel['name']) + ": New Video - " + playlist_item["snippet"]["title"]
            # Post it
            wordpress.post(wp, site_libraries[0], site_libraries[1], playlist_item["snippet"]["title"], post_content, playlist_item["snippet"]["publishedAt"], playlist_item["snippet"]["resourceId"]["videoId"], {'post_tag': tags ,'category': category})

            # add it to the known videos
            known_channel.append(playlist_item["snippet"]["resourceId"]["videoId"])

            added_videos += 1

            site_libraries = wordpress.updateLibraries(wp)

    return known_channel


def cycle(init=False):
    global added_videos

    # Fetch videos of unknown channels and register the channels in knownvideos.json
    for channel in channels:
	if channel['active'] == False:
		continue

        added_videos = 0
        # print "Fetching Videos in list of Channel %s" % channel['name']
        videosresponse = getyoutubevideos.catchChannelVideos(service, str(channel['id']))

        channel_is_known = False
        for known_channel in knownvideos:
            #print "%s compared with %s", (str(known_channel[0]), str(channel['id']))
            if str(known_channel[0]) == str(channel['id']):
                #print "Channel already registered!"
                channel_is_known = True
                known_channel = handle_video(channel, videosresponse, known_channel)

        if channel_is_known == False:

            add_existing_videos = False
            if init == True:
                if raw_input("Unkown Channel \"" + channel['name']  + "\". Add all exisiting videos to the website? [y/N]") == 'y':
                    add_existing_videos = True

            new_channel = []
            set(new_channel)
            new_channel.append(str(channel['id'])) # Add channel ID first, so we know what channel the videos belong to
            if add_existing_videos:
                new_channel = handle_video(channel, videosresponse, new_channel)

            knownvideos.append(new_channel)
            log_message(">>> Added " + channel['name'] + " as new channel to known channels!")

        if added_videos > 0:
            log_message(">>> Added " + str(added_videos) + " new videos of " + str(channel['name']) + " to the website!")

    #print knownvideos

    # Save knownvideos in knownvideos.json
    knownvideos_file_write = open(KNOWNVIDEOS_FILENAME, 'w')
    json.dump(knownvideos, knownvideos_file_write)
    knownvideos_file_write.close()

def log_message(msg):
    msg = str(datetime.datetime.now()) + ": " + msg
    log_file = open(LOG_FILENAME, "a")
    log_file.write(msg + "\n")
    log_file.close()
    print (msg)


# Here the actual main loop
#log_message("Server started! Initial run...")
log_message("Script started!")
wp = wordpress.login(channels[0]['user'],channels[0]['password'])
site_libraries = wordpress.updateLibraries(wp)
cycle(True)
log_message("Script complete!")


#while True:
    #try:
    	#print "Done! Now waiting " + str(WAIT_TIME) + " seconds!"
    	#time.sleep(WAIT_TIME)
	#cycle()
    #except BaseException:
        #log_message("HALTING SCRIPT: An Exception was thrown!")
	#log_message(traceback.format_exc())
		
        #print "Exiting..."
        #quit()

