import discord


class DiscordBBcodeCompiler():

    PARSE_END   = -1
    PARSE_BEGIN = 0
    PARSE_NEXT  = 1

    def Compile(self, text, posts):
        self.buffer_size = 2048
        self.posts = posts; self.beg = 0

        compile_state = self.PARSE_BEGIN
        
        while compile_state != self.PARSE_END:
            self.end = min(len(text), self.beg + self.buffer_size)
            if self.beg >= self.end: break

            self.embed = discord.Embed(type='rich', color=0x66CC66)
            self.buffer = text[self.beg:self.end]
            
            if self.parseImage()           == self.PARSE_BEGIN: continue
            if self.parseImageSecure()     == self.PARSE_BEGIN: continue
            if self.parseVideo()           == self.PARSE_BEGIN: continue
            if self.parseText()            == self.PARSE_BEGIN: continue
            if self.parseHyperlink()       == self.PARSE_BEGIN: continue
            if self.parseHyperlinkSecure() == self.PARSE_BEGIN: continue
            if self.parseNewline()         == self.PARSE_BEGIN: continue
            if self.parseContentChar()     == self.PARSE_BEGIN: continue
            if self.parseDefault()         == self.PARSE_BEGIN: continue

        return self.posts


    # TODO: Figure out how to simplify all into a genric method
    def parseToken(self, token_begin, token_end, token_replace):
        # If found, then check if there is something to record before that
        idx = self.buffer.find(token_begin, 0, len(self.buffer))
        if idx != -1:
            #print("img")
            if idx == 0:
                idx = self.buffer.find(token_end, 0, self.end)
                self.embed.set_image(url=self.buffer[0:idx].replace(token_begin, token_end))
            else:
                self.embed.description = self.buffer[0:idx].replace(token_end,'').strip()
                if self.embed.description: self.posts.append(self.embed)

            self.beg += idx
            return self.PARSE_BEGIN

    
    def parseImage(self):
        # If found, then check if there is something to record before that
        idx = self.buffer.find('img://', 0, len(self.buffer))
        if idx != -1:
            #print("img")
            if idx == 0:
                idx = self.buffer.find('\x03', 0, self.end)
                self.embed.set_image(url=self.buffer[0:idx].replace('img','http'))
            else:
                self.embed.description = self.buffer[0:idx].replace('\x03','').strip()
                if self.embed.description: self.posts.append(self.embed)

            self.beg += idx
            return self.PARSE_BEGIN


    def parseImageSecure(self):
        # If found, then check if there is something to record before that
        idx = self.buffer.find('imgs://', 0, len(self.buffer))
        if idx != -1: 
            #print("imgs")
            if idx == 0: # Record img
                idx = self.buffer.find('\x03', 0, self.end)
                self.embed.set_image(url=self.buffer[0:idx].replace('imgs','https'))
                #print(buffer[0:idx])
                self.posts.append(self.embed)
            else:
                self.embed.description = self.buffer[0:idx].replace('\x03','').strip()
                if self.embed.description: self.posts.append(self.embed)
            
            self.beg += idx
            return self.PARSE_BEGIN


    def parseVideo(self):
        # If found, then see if we can get the link's end. If not, get everything prior
        idx = self.buffer.rfind('vids://', 0, len(self.buffer))
        if idx != -1:
            #print("vids")
            link_end = self.buffer.rfind('\x03', 0, self.end)
            if link_end != -1: idx = link_end

            self.embed.description = self.buffer[0:idx].replace('vids','https').replace('\x03','').strip()
            if self.embed.description: self.posts.append(self.embed)
            self.beg += idx
            return self.PARSE_BEGIN


    def parseText(self):
        # If the post fits well below the lenth, just record it. 
        # Otherwise, start looking at the best way to split it up
        if len(self.buffer) < (self.buffer_size - 200):
            #print("just recorded")
            self.embed.description = self.buffer[0:len(self.buffer)].replace('\x03','').strip()
            if self.embed.description: self.posts.append(self.embed)
            self.beg += len(self.buffer)
            return self.PARSE_BEGIN


    def parseHyperlink(self):
        # If found, then see if we can get the link's end. If not, get everything prior
        idx = self.buffer.rfind('http://', 0, len(self.buffer))
        if idx != -1: 
            #print("http")
            link_end = self.buffer.rfind('\x03', 0, self.end)
            if link_end != -1: idx = link_end

            self.embed.description = self.buffer[0:idx].replace('\x03','').strip()
            if self.embed.description: self.posts.append(self.embed)
            self.beg += idx
            return self.PARSE_BEGIN


    def parseHyperlinkSecure(self):
        # If found, then see if we can get the link's end. If not, get everything prior
        idx = self.buffer.rfind('https://', 0, len(self.buffer))
        if idx != -1:
            #print("https")
            link_end = self.buffer.rfind('\x03', 0, self.end)
            if link_end != -1: idx = link_end

            self.embed.description = self.buffer[0:idx].replace('\x03','').strip()
            if self.embed.description: self.posts.append(self.embed)
            self.beg += idx
            return self.PARSE_BEGIN


    def parseNewline(self):
        # If found, then record the range
        idx = self.buffer.rfind('\n', 0, len(self.buffer))
        if idx != -1:
            #print("NL")
            self.embed.description = self.buffer[0:idx].replace('\x03','').strip()
            if self.embed.description: self.posts.append(self.embed)
            self.beg += idx + 1
            return self.PARSE_BEGIN


    def parseContentChar(self):
        # If found, then record the range
        idx = self.buffer.rfind(' ', 0, len(self.buffer))
        if idx != -1: 
            #print("space")
            self.embed.description = self.buffer[0:idx].replace('\x03','').strip()
            if self.embed.description: self.posts.append(self.embed)
            self.beg += idx + 1
            return self.PARSE_BEGIN


    def parseDefault(self):
        self.embed.description = self.buffer.replace('\x03','').strip()
        if self.embed.description: self.posts.append(self.embed)
        self.beg += len(self.buffer)
        return self.PARSE_BEGIN