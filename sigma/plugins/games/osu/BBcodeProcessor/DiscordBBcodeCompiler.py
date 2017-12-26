import discord


class DiscordBBcodeCompiler():

    BUFFER_SIZE = 2048

    def Compile(self, text, posts):
        if self.parseImage(text, posts):       return
        if self.parseSecureImage(text, posts): return
        if self.parseVideo(text, posts):       return
        if self.parseLink(text, posts):        return
        if self.parseSecureLink(text, posts):  return
        if self.parseNewline(text, posts):     return
        if self.parseSpace(text, posts):       return
        if self.parseText(text, posts):        return


    def parseImage(self, text, posts):
        token_len = len('img://')
        beg = text.rfind('img://', 0, self.BUFFER_SIZE + token_len)
        if beg == -1: return False

        token_len = 1
        end = min(text.find(' ', beg), text.find('\n', beg))
        if end == -1 or end ==  0: return False

        self.Compile(text[:beg], posts)

        content = text[beg:end + token_len].replace('img','http').strip()
        if content:
            print('DiscordBBcodeCompiler.py : parseImage')

            embed = discord.Embed(type='rich', color=0x66CC66)
            embed.set_image(url=content)
            posts.append(embed)

        self.Compile(text[end + token_len:], posts)
        return True


    def parseSecureImage(self, text, posts):
        token_len = len('imgs://')
        beg = text.rfind('imgs://', 0, self.BUFFER_SIZE + token_len)
        if beg == -1: return False

        token_len = 1
        end = min(text.find(' ', beg), text.find('\n', beg))
        if end == -1 or end ==  0: return False

        self.Compile(text[:beg], posts)

        content = text[beg:end + token_len].replace('imgs','https').strip()
        if content:
            print('DiscordBBcodeCompiler.py : parseSecureImage')
            print(content)

            embed = discord.Embed(type='rich', color=0x66CC66)
            embed.set_image(url=content)
            posts.append(embed)

        self.Compile(text[end + token_len:], posts)
        return True

    
    def parseVideo(self, text, posts):
        token_len = len('vids://')
        beg = text.rfind('vids://', 0, self.BUFFER_SIZE + token_len)
        if beg == -1: return False

        token_len = 1
        end = min(text.find(' ', beg), text.find('\n', beg))
        if end == -1 or end ==  0: return False

        self.Compile(text[:beg], posts)

        content = text[beg:end + token_len].replace('vids','https').strip()
        if content:
            print('DiscordBBcodeCompiler.py : parseVideo')

            embed = discord.Embed(type='rich', color=0x66CC66)
            embed.description = content
            posts.append(embed)

        self.Compile(text[end + token_len:], posts)
        return True
    

    def parseLink(self, text, posts):
        token_len = len('http://')
        beg = text.rfind('http://', 0, self.BUFFER_SIZE + token_len)
        if beg == -1: return False

        token_len = 1
        end = min(text.find(' ', beg), text.find('\n', beg))
        if end < self.BUFFER_SIZE: return False

        self.Compile(text[:beg], posts)
        
        content = text[beg:end + token_len].strip()
        if content:
            print('DiscordBBcodeCompiler.py : parseLink')

            embed = discord.Embed(type='rich', color=0x66CC66)
            embed.description = content
            posts.append(embed)

        self.Compile(text[end + token_len:], posts)
        return True


    def parseSecureLink(self, text, posts):
        token_len = len('https://')
        beg = text.rfind('https://', 0, self.BUFFER_SIZE + token_len)
        if beg == -1: return False

        token_len = 1
        end = min(text.find(' ', beg), text.find('\n', beg))
        if end < self.BUFFER_SIZE: return False

        self.Compile(text[:beg], posts)

        content = text[beg:end + token_len].strip()
        if content:
            print('DiscordBBcodeCompiler.py : parseSecureLink')

            embed = discord.Embed(type='rich', color=0x66CC66)
            embed.description = content
            posts.append(embed)

        self.Compile(text[end + token_len:], posts)
        return True


    def parseNewline(self, text, posts):
        token_len = len('\n')
        beg = 0
        if beg == -1: return False

        end = text.rfind('\n', 0, self.BUFFER_SIZE + token_len)
        if end < self.BUFFER_SIZE - 25: return False
        
        content = text[beg:end + token_len].strip()
        if content:
            print('DiscordBBcodeCompiler.py : parseNewline')

            embed = discord.Embed(type='rich', color=0x66CC66)
            embed.description = content
            posts.append(embed)

        self.Compile(text[end + token_len:], posts)
        return True

    
    def parseSpace(self, text, posts):
        token_len = len(' ')
        beg = 0
        if beg == -1: return False

        end = text.rfind(' ', 0, self.BUFFER_SIZE + token_len)        
        if end < self.BUFFER_SIZE - 25: return False
        
        content = text[beg:end + token_len].strip()
        if content:
            print('DiscordBBcodeCompiler.py : parseSpace')

            embed = discord.Embed(type='rich', color=0x66CC66)
            embed.description = content
            posts.append(embed)

        self.Compile(text[end + token_len:], posts)
        return True


    def parseText(self, text, posts):
        token_len = len('')
        
        beg = 0
        if beg == -1: return False

        end = text.rfind('', 0, self.BUFFER_SIZE + token_len)
        if end == -1 or end ==  0: return False
        
        content = text[beg:end].strip()
        if content:
            print('DiscordBBcodeCompiler.py : parseText')

            embed = discord.Embed(type='rich', color=0x66CC66)
            embed.description = content
            posts.append(embed)

        self.Compile(text[end + token_len:], posts)
        return True