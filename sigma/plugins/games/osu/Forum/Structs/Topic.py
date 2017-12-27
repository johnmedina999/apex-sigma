from bs4 import BeautifulSoup
from .User import User
from .Post import Post

class Topic():

    def __init__(self, root=None):
        self.subforum = None
        self.creator  = None
        self.posts    = []
        self.name     = None
        self.date     = None
        self.url      = None

        if not root: return
        
        self.getSubforum(root)
        self.getCreator(root)
        self.getPosts(root, True)
        self.getName(root)
        self.getDate(root)
        self.getUrl(root)


    def getSubforum(self, root=None):
        if not self.subforum:
            self.subforum = root.find_all(class_='page-mode-link--is-active')[0].text.strip()
        
        return self.subforum

    
    def getDate(self, root=None):
        if not self.date:
            posts = root.find_all(class_='forum-post')
            for post in posts: self.posts.append(Post(self, post))
            
            self.date    = self.posts[0].getDate()
            self.creator = self.posts[0].getCreator.getName()
            
        return self.date

    
    def getName(self, root=None):
        if not self.name:
           name = root.find_all(class_='js-forum-topic-title--title')[0]
           self.url  = name['href'].strip()
           self.name = name.text.strip()
           
        return self.name


    def getUrl(self, root=None):
        if not self.url:
            name = root.find_all(class_='js-forum-topic-title--title')[0]
            self.name = name.text.strip()
            self.url  = name['href'].strip()
            
        return self.url


    def getCreator(self, root=None):
        if not self.creator:
            posts = root.find_all(class_='forum-post')
            for post in posts: self.posts.append(Post(self, post))
            
            self.date    = self.posts[0].getDate()
            self.creator = self.posts[0].getCreator()
        
        return self.creator


    def getPosts(self, root=None, first_only=False):
        if len(self.posts) == 0:
            posts = root.find_all(class_='forum-post')

            if first_only == True: 
                self.posts.append(Post(self, posts[0]))
                self.date    = self.posts[0].getDate()
                self.creator = self.posts[0].getCreator()
            else:
                for post in posts[1:]: self.posts.append(Post(self, post))
            
        return self.posts

    
