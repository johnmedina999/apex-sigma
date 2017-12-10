from bs4 import BeautifulSoup

class BBcodeProcessor():

    def Process(self, post_contents):

        code = BeautifulSoup(post_contents, "lxml")

        self.procNewline(code)
        self.procHeading(code)
        self.procListIndicator(code)
        self.procListIndicator(code)
        self.procCentredFormatting(code)
        self.procListBullet(code)
        self.procVideoFrame(code)
        self.procSpoilerBoxArrow(code)
        self.procSpoilerBoxHeader(code)
        self.procEmoji(code)
        self.procImage(code)
        self.procHyperlink(code)
        self.procQuoteHeader(code)
        self.procBlockQuote(code)
        self.procBoldFormatting(code)
        self.procUnderlineFormatting(code)
        self.procDivWell(code)

        return code


    # TODO: Figure out how to simplify all into a generic method
    def processBBcode(self, element, content, before_elem='', after_elem=''):
        while True:
            try:
                if element.get_text():
                    element.insert_before(before_elem)
                    element.insert_after(after_elem)
                element.unwrap()
            except: break


    def procNewline(self, code):
        while True:
            try: # Next lines
                code.br.insert_before('\n')
                code.br.unwrap()
            except: break


    def procHeading(self, code):
        while True:
            try: # Heading 2
                code.h2.insert_before('\n\n')
                code.h2.insert_after('\n')
                code.h2.unwrap()
            except: break


    def procListIndicator(self, code):
        while True:
            try: # List indicator; ignore
                code.ol.unwrap()
            except: break


    def procCentredFormatting(self, code):
        while True:
            try: # Centered text
                if code.center.get_text():
                    code.center.insert_before('\n')
                    code.center.insert_after('\n')
                code.center.unwrap()
            except: break


    def procListBullet(self, code):
        while True:
            try: # List bullets
                if code.li.get_text():
                    code.li.insert_before('\n    ● ')
                code.li.unwrap()
            except: break


    def procVideoFrame(self, code):
        while True:
            try: # Replace https with vid so we can easily identify Youtube video links later on
                code.iframe.insert_before(code.iframe['src'].replace('http','vid') + '\x03')
                code.iframe.unwrap()
            except: break

    
    def procSpoilerBoxArrow(self, code):
        while True:
            try: # Spoiler box arrow
                code.select_one("i.fa.fa-chevron-down.bbcode-spoilerbox__arrow").unwrap()
            except: break


    def procSpoilerBoxHeader(self, code):
        while True:
            try: # Spoiler box open/close thingy
                code.select_one("div.bbcode-spoilerbox__body").insert_before(':\n ')
                code.select_one("div.bbcode-spoilerbox__body").insert_after('\n')
                code.select_one("div.bbcode-spoilerbox__body").unwrap()
            except: break


    def procEmoji(self, code):
        while True:
            try: # Emojis
                emoji = code.select_one("img.smiley")
                if emoji['title'] == 'smile': emoji.insert_after(':smile:')
                if emoji['title'] == 'wink': emoji.insert_after(':wink:')
                if emoji['title'] == 'Grin': emoji.insert_after(':grin:')
                if emoji['title'] == 'cry': emoji.insert_after(':cry:')
                emoji.unwrap()
            except: break


    def procImage(self, code):
        while True:
            try: # Images
            
                try: # For any missed emoji
                    if code.img['class'] == ['smiley']: 
                        #cmd.log.warning("[ get_thread ] Smiley not handled: " + code.img)
                        code.img.unwrap()
                        continue
                except: pass

                # Replace https with img so we can easily identify image links later on
                if code.img['data-normal']: code.img.insert_before(code.img['data-normal'].replace('http','img') + '\x03')
                elif code.img['src']:       code.img.insert_before(code.img['src'].replace('http','img') + '\x03')

                code.img.unwrap()
            except: break


    def procHyperlink(self, code):
        while True:
            try: # Add markdown for it to be a hyperlink
                try: code.a.insert_before('[' + code.a.text.replace('[', '\[').replace(']', '\]') + ']' +
                                          '(' + code.a['href'].replace('(', '\(').replace(')', '\)') + ')\x03')
                except: pass

                code.a.clear()
                code.a.unwrap()
            except: break


    def procQuoteHeader(self, code):
        while True:
            try: # Bold text
                text = code.h4.get_text()
                if text: # Need to make sure the start and ends of seperate formatting blocks don't touch
                    if text[0] == ' ': text = ' **' + text[1:]
                    else:              text = '**' + text

                    if text[-1] == ' ': text = text[:-1] + '** '
                    else:               text = text + '**'
                
                    code.h4.insert_before(text + '\n')
            
                code.h4.clear()
                code.h4.unwrap()
            except: break


    def procBlockQuote(self, code):
        while True:
            try:
                text = ''
                for child in list(code.blockquote.children):
                    try:  text += child
                    except:
                        try: text += BBcodeProcessor().Process(str(child)).text
                        except: break

                text = ''.join(['**|**    ' + line + '\n' for line in text.split('\n')])
                code.blockquote.insert_before(text + '\n')

                code.blockquote.clear()
                code.blockquote.unwrap()
                
            except: break


    # Italic/underline/bold processing needs to go after url processing (discord doesn't like [**text**](url), but will accept **[text](url)**)
    def procBoldFormatting(self, code):
        while True:
            try: # Bold text
                text = code.strong.get_text()
                if text: # Need to make sure the start and ends of seperate formatting blocks don't touch
                    if text[0] == ' ': text = ' **' + text[1:]
                    else:              text = '**' + text

                    if text[-1] == ' ': text = text[:-1] + '** '
                    else:               text = text + '**'
                
                    code.strong.insert_before(text)
            
                code.strong.clear()
                code.strong.unwrap()
            except: break


    def procUnderlineFormatting(self, code):
        while True:
            try: # Underline text
                text = code.u.get_text()
                if text: # Need to make sure the start and ends of seperate formatting blocks don't touch
                    if text[0] == ' ': text = ' __' + text[1:]
                    else:              text = '__' + text

                    if text[-1] == ' ': text = text[:-1] + '__ '
                    else:               text = text + '__'
                
                    code.u.insert_before(text)
            
                code.u.clear()
                code.u.unwrap()
            except: break


    def procItalicFormatting(self, code):
        while True:
            try: # Italic text
                text = code.em.get_text()
                if text: # Need to make sure the start and ends of seperate formatting blocks don't touch
                    if text[0] == ' ': text = ' *' + text[1:]
                    else:              text = '*' + text

                    if text[-1] == ' ': text = text[:-1] + '* '
                    else:               text = text + '*'
                
                    code.em.insert_before(text)
            
                code.em.clear()
                code.em.unwrap()
            except: break


    def procDivWell(self, code):
        while True:
            try:
                code.select_one("div.well").insert_before('\n\n')
                code.select_one("div.well").unwrap()
            except: break