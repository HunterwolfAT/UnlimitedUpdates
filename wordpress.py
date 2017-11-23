from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.compat import xmlrpc_client 
from datetime import datetime
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

def post(client, media_library, posts, title, content, date_posted, video_id, terms):

    # Check if the post already exists
    for post in posts:
        if post.title == title:
            print 'Post already exists!'
            return # We are done here

    print "Adding Video " + title + "..."
    post = WordPressPost()
    post.title = title
    post.content = content
    post.terms_names = terms 
    post.date = datetime.strptime(date_posted, '%Y-%m-%dT%H:%M:%S.%fZ')

    # Check if the thumbnail already exists in the media library
    thumbnail_exists = False

    for entry in media_library:
        if entry.title == 'thumbnail_' + video_id + '.jpg':
            print "Thumbnail already exists!"
            thumbnail_id = entry.id
            thumbnail_exists = True
            break
        

    if not thumbnail_exists:
        # Download the YouTube thumbnail and place it with the the other wordpress media
        print "Download Thumbnail..."
        image = urllib2.urlopen("https://img.youtube.com/vi/" + video_id + "/sddefault.jpg").read()
        data = {
                'name': 'thumbnail_' + video_id + '.jpg',
                'type': 'image/jpeg',
        }
        data['bits'] = xmlrpc_client.Binary(image)

        return_data = client.call(media.UploadFile(data))
        thumbnail_id = return_data['id']

    # Set the thumbnail as the featured image of the post
    post.thumbnail = thumbnail_id

    post.post_status = 'publish'
    client.call(NewPost(post))

    print "Upload successfull!"
