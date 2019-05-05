from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.compat import xmlrpc_client 
from datetime import datetime
from pprint import pprint
import urllib2

def login(user, password):
    wp = Client('http://127.0.0.1/xmlrpc.php', user, password)
    return wp

def updateLibraries(client):
    print "Updating local media library..."
    filter_data = {'mime_type': 'image/jpeg'}
    media_lib = client.call(media.GetMediaLibrary(filter_data))
    posts_lib = client.call(GetPosts([]))
    all_libs = [ media_lib, posts_lib ]
    return all_libs

def printPost(post):
    if hasattr(post, 'title'):
    	print("==========================Title========================")
	print(post.title)
    else:
	print("NO TITLE!")
    if hasattr(post, 'content'):
    	print("=======================Content==========================")
	print(post.content)
    else:
	print("NO CONTENT!")
    if hasattr(post, 'terms_names'):
	print "========================Terms==========================="
	for term in post.terms_names:
	    print(term)
    else:
	print("NO TERMS!")
    if hasattr(post, 'date'):
    	print("=========================Date=========================")
	print(post.date)
    else:
	print("NO DATE!")
    if hasattr(post, 'custom_fields'):
	print("=====================Custom Fields====================")
	for field in post.custom_fields:
	    print(field)
    else:
	print("NO CUSTOM FIELDS!")
    if hasattr(post, 'thumbnail'):
    	print("=====================Thumbnail=========================")
	print(post.thumbnail)
    else:
	print("NO THUMBNAIL!")


def post(client, media_library, posts, title, content, date_posted, video_id, terms):

    # Check if the post already exists
    for post in posts:
        if post.title == title:
            print 'Post already exists!'
            return # We are done here

    print "Adding Video " + title.encode('utf-8', 'ignore') + "..."
    post = WordPressPost()
    # print "==================== Post status right after creation ======================"
    # pprint(post.__dict__)
    post.title = title
    post.content = content
    post.terms_names = terms 
    post.date = datetime.strptime(date_posted, '%Y-%m-%dT%H:%M:%S.%fZ')

    # Set the video url as a custom field
    url = "https://www.youtube.com/watch?=" + video_id
    post.custom_fields = []
    post.custom_fields.append({'key' : 'youtubeurl', 'value' : url})

    # Check if the thumbnail already exists in the media library
    thumbnail_exists = False

    for entry in media_library:
        if entry.title == 'thumbnail_' + video_id + '.jpg':
            print("Thumbnail already exists!")
            post.thumbnail = entry.id
            thumbnail_exists = True
            break
        

    if not thumbnail_exists:
        # Download the YouTube thumbnail and place it with the the other wordpress media
        print "Download Thumbnail..."
        try:
            image = urllib2.urlopen("https://img.youtube.com/vi/" + video_id + "/sddefault.jpg").read()
        except urllib2.HTTPError:
            try:
                image = urllib2.urlopen("https://img.youtube.com/vi/" + video_id + "/hqdefault.jpg").read()
            except urllib2.HTTPError:
		try:
			image = urllib2.urlopen("https://img.youtube.com/vi/" + video_id + "/maxresdefault.jpg").read()
		except urllib2.HTTPError:
			print "FEHLER: KONNTE YOUTUBE THUMBNAIL NICHT AUSFINDIG MACHEN"

        data = {
                'name': 'thumbnail_' + video_id + '.jpg',
                'type': 'image/jpeg',
        }
        data['bits'] = xmlrpc_client.Binary(image)
	pprint(data)

        return_data = client.call(media.UploadFile(data))
	if not return_data == '':
        	thumbnail_id = return_data['id']
		# Set the thumbnail as the featured image of the post
    		post.thumbnail = return_data['id']
	else:
		print "FEHLER: THUMBNAIL KONNTE NICHT IN WORDPRESS IMPORTIERT WERDEN"

    # Only publish post if it successfully got an image
    post.post_status = 'publish'
    print "Post object just before sending it to wordpress."
    pprint(post.__dict__)
    wpResult = client.call(NewPost(post))

    if not wpResult == '':
    	print "Upload successfull!"
	return True
    else:
	print "ERROR: Upload Fehlgeschlagen!"
	return False
