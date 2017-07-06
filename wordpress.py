from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
import wordpress_xmlrpc


def login(user, password):
    wp = Client('http://127.0.0.1/xmlrpc.php', user, password)
    return wp

def post(client, title, content, terms):
    post = WordPressPost()
    post.title = title
    post.content = content
    post.terms_names = terms #{
            #'post_tag': ['python', 'really cool'],
            #'category': ['Internal']
    #}
    # TODO: uncomment to actually make things visible
    #post.post_status = 'publish'
    client.call(NewPost(post))
