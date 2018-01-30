from bs4 import BeautifulSoup
from .User import User


class Post():

    def __init__(self, topic, root=None):
        self.topic    = topic
        self.creator  = None
        self.contents = None
        self.date     = None
        self.url      = None

        if not root: return
        
        self.getCreator(root)
        self.getContents(root)
        self.getDate(root)
        self.getUrl(root)


    def getTopic(self):
        return self.topic


    def getCreator(self, root=None):
        if not self.creator:
            self.creator = User(root)
        
        return self.creator


    def getContents(self, root=None):
        if not self.contents:
            post_body = root.find_all(class_='forum-post__body')[0]
            self.url = str(post_body.find_all(class_='js-post-url')[0]['href'])
            self.contents = str(post_body.find_all(class_='forum-post-content ')[0])
        
        return self.contents


    def getDate(self, root=None):
        if not self.date:
            self.date = root.find_all(class_='timeago')[0].text.strip()
            
        return self.date


    def getUrl(self, root=None):
        if not self.url:
            post_body = root.find_all(class_='forum-post__body')[0]
            self.contents = str(post_body.find_all(class_='forum-post-content ')[0]).strip()
            self.url = str(post_body.find_all(class_='js-post-url')[0]['href']).strip()
        
        return self.url