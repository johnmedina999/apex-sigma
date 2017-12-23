from bs4 import BeautifulSoup
import re


class User():

    def __init__(self, root=None):
        self.name   = None
        self.avatar = None
        self.url    = None

        if not root: return
        
        self.getName(root)
        self.getAvatar(root)
        self.getUrl(root)


    def getName(self, root=None):
        if not self.name:
            try: self.name = root.find_all(class_='forum-post__username')[0].text.strip()
            except: self.name = ""
            if not self.name: self.name = ""

        return self.name


    def getAvatar(self, root=None):
        if not self.avatar:
            try: post_poster_avatar = root.find_all(class_='avatar avatar--forum')[0].get('style')
            except: post_poster_avatar = "background-image: url('');"
           
            if not post_poster_avatar: post_poster_avatar = "background-image: url('');"
            self.avatar = re.findall('background-image: url\(\'(.*?)\'\);', post_poster_avatar)[0]
        
        return self.avatar

    
    def getUrl(self, root=None):
        if not self.url:
            try: self.url = root.find_all(class_='forum-post__username')[0].get('href')
            except: self.url = "https://osu.ppy.sh/users/-1"
            if not self.url: post_poster_url = "https://osu.ppy.sh/users/-1"

            
        return self.url