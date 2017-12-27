from bs4 import BeautifulSoup
import textwrap

class BBcodeProcessor():
    # BUG: All current logic erases tags that are nested within tags. Implement a similiar thing as done with quote blocks to fix
    def Process(self, post_contents):

        self.sanitize(post_contents)
        code = BeautifulSoup(post_contents, "lxml")

        self.procNewline(code)
        self.procHeading(code)
        self.procListIndicator(code)
        self.procListTitle(code)
        self.procListIndicator(code)
        self.procCentredFormatting(code)
        self.procVideoFrame(code)
        self.procSpoilerBoxArrow(code)
        self.procSpoilerBoxHeader(code)
        self.procEmoji(code)
        self.procImage(code)
        self.procHyperlink(code)
        self.procQuoteHeader(code)
        self.procBlockQuote(code)
        self.procBoldFormatting(code)
        self.procStrikelineFormatting(code)
        self.procUnderlineFormatting(code)
        self.procItalicFormatting(code)
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


    def sanitize(self, code):
        sanitizations = [ ('*', '\*'), ('_', '\_') ]
        for sanitization in sanitizations:
            code.replace(sanitization[0], sanitization[1])

        return code


    # Recursively processes the BBcode
    def processBBcodeChildren(self, children):
        text = ''
        for child in list(children):
            # Text to wrap a certain amount of lines since discord rich text wraps it, and '|' will not show on that new line
            try:  text += textwrap.fill(child, width=75, drop_whitespace=False, replace_whitespace=False)
            except:
                # If we couldn't append text, then it's unprocessed HTML code
                try: text += BBcodeProcessor().Process(str(child)).text
                except: break
        
        return text
    

    def procNewline(self, code):
        while True:
            subcode = code.select_one(self.sanitize('br'))
            if not subcode: break

            subcode.insert_before('\n')
            subcode.clear()
            subcode.unwrap()


    def procHeading(self, code):
        while True:  # Heading 2
            subcode = code.select_one(self.sanitize('h2'))
            if not subcode: break

            text = self.processBBcodeChildren(subcode.children)
            if text: subcode.insert_before('\n\n' + text + '\n')
            
            subcode.clear()
            subcode.unwrap()


    def procCentredFormatting(self, code):
        while True:  # Centered text
            subcode = code.select_one(self.sanitize('center'))
            if not subcode: break

            text = self.processBBcodeChildren(subcode.children)
            if text: subcode.insert_before('\n' + text + '\n')

            subcode.clear()
            subcode.unwrap()


    def procListTitle(self, code):
        while True:
            subcode = code.select_one(self.sanitize('ul.bbcode__list-title'))
            if not subcode: break

            text = self.processBBcodeChildren(subcode.children)
            text = ''.join(['    ' + line for line in text.splitlines(True)])

            subcode.insert_before(text)
            subcode.clear()
            subcode.unwrap()


    def procListIndicator(self, code):
        while True:  # List indicator
            subcode = code.select_one(self.sanitize('ol.unordered'))
            if not subcode: break

            while True:  # Process bullets
                bullet = subcode.select_one(self.sanitize('li'))
                if not bullet: break

                text = self.processBBcodeChildren(bullet.children)
                if text:
                    bullet.insert_before('●  ' + text + '\n')
                    bullet.clear()
                    bullet.unwrap()

            text = self.processBBcodeChildren(subcode.children)
            text = ''.join(['    ' + line for line in text.splitlines(True)])

            subcode.insert_before(text)
            subcode.clear()
            subcode.unwrap()


    def procVideoFrame(self, code):
        while True:  # Replace https with vid so we can easily identify Youtube video links later on
            subcode = code.select_one(self.sanitize('iframe'))
            if not subcode: break

            text = subcode['src']
            if text:
                subcode.insert_before(text.replace('http','vid').replace('embed/', 'watch?v=').replace('?rel=0', '') + ' ')

            subcode.clear()
            subcode.unwrap()

    
    def procSpoilerBoxArrow(self, code):
        while True:
            try: # Spoiler box arrow
                code.select_one(self.sanitize('i.bbcode-spoilerbox__arrow')).unwrap()
            except: break

            subcode.clear()
            subcode.unwrap()


    def procSpoilerBoxHeader(self, code):
                
            subcode.clear()
            subcode.unwrap()
        while True:
            try: # Spoiler box open/close thingy
                code.select_one("div.bbcode-spoilerbox__body").insert_before(':\n ')
                code.select_one("div.bbcode-spoilerbox__body").insert_after('\n')
                code.select_one("div.bbcode-spoilerbox__body").unwrap()
            except: break

            subcode.clear()
            subcode.unwrap()


    def procEmoji(self, code):
        while True:
            subcode = code.select_one(self.sanitize('img.smiley'))
            if not subcode: break

            text = subcode['alt']
            subcode.insert_before(text + ' ')

            subcode.clear()
            subcode.unwrap()


    def procImage(self, code):
        while True: # Images
            subcode = code.select_one(self.sanitize('img.proportional-container__content'))
            if not subcode: break

            # Replace https with img so we can easily identify image links later on
            if subcode['data-normal']: text = subcode['data-normal']
            elif subcode['src']:       text = subcode['src']

            subcode.insert_before(text.replace('http','img') + ' ')

            subcode.clear()
            subcode.unwrap()


    def procHyperlink(self, code):
        while True:  # Add markdown for it to be a hyperlink
            subcode = code.select_one(self.sanitize('a'))
            if not subcode: break

            subcode.insert_before('[' + subcode.text.replace('[', '\[').replace(']', '\]') + ']' +
                                  '(' + subcode['href'].replace('(', '\(').replace(')', '\)') + ') ')
            subcode.clear()
            subcode.unwrap()


    def procQuoteHeader(self, code):
        while True:
            subcode = code.select_one(self.sanitize('h4'))
            if not subcode: break

            text = self.processBBcodeChildren(subcode.children)
            if text: # Need to make sure the start and ends of seperate formatting blocks don't touch
                if text[0] == ' ': text = ' **' + text[1:]
                else:              text = '**' + text

                if text[-1] == ' ': text = text[:-1] + '** '
                else:               text = text + '**'
                
                subcode.insert_before(text + '\n\n')
            
            subcode.clear()
            subcode.unwrap()


    def procBlockQuote(self, code):
        while True:
            subcode = code.select_one(self.sanitize('blockquote'))
            if not subcode: break

            text = self.processBBcodeChildren(subcode.children)
            text = ''.join(['**|**    ' + line + '\n' for line in text.split('\n')])
            subcode.insert_before(text + '\n')

            subcode.clear()
            subcode.unwrap()


    # Italic/underline/bold processing needs to go after url processing (discord doesn't like [**text**](url), but will accept **[text](url)**)
    def procBoldFormatting(self, code):
        while True:  # Bold text
            subcode = code.select_one(self.sanitize('strong'))
            if not subcode: break

            text = self.processBBcodeChildren(subcode.children)
            if text: # Need to make sure the start and ends of seperate formatting blocks don't touch
                if text[0] == ' ': text = ' **' + text[1:]
                else:              text = '**' + text

                if text[-1] == ' ': text = text[:-1] + '** '
                else:               text = text + '**'

                subcode.insert_before(text)
            
            subcode.clear()
            subcode.unwrap()


    def procUnderlineFormatting(self, code):
        while True:
            subcode = code.select_one(self.sanitize('u'))
            if not subcode: break

            text = self.processBBcodeChildren(subcode.children)
            if text: # Need to make sure the start and ends of seperate formatting blocks don't touch
                if text[0] == ' ': text = ' __' + text[1:]
                else:              text = '__' + text

                if text[-1] == ' ': text = text[:-1] + '__ '
                else:               text = text + '__'
                
                subcode.insert_before(text)
            
            subcode.clear()
            subcode.unwrap()


    def procStrikelineFormatting(self, code):
        while True:  # Strikeline text
            subcode = code.select_one(self.sanitize('del'))
            if not subcode: break

            text = self.processBBcodeChildren(subcode.children)
            if text: # Need to make sure the start and ends of seperate formatting blocks don't touch
                if text[0] == ' ': text = ' ~~' + text[1:]
                else:              text = '~~' + text

                if text[-1] == ' ': text = text[:-1] + '~~ '
                else:               text = text + '~~'
                
                subcode.insert_before(text)
            
            subcode.clear()
            subcode.unwrap()


    def procItalicFormatting(self, code):
        while True:  # Italic text
            subcode = code.select_one(self.sanitize('em'))
            if not subcode: break

            text = self.processBBcodeChildren(subcode.children)
            if text: # Need to make sure the start and ends of seperate formatting blocks don't touch
                if text[0] == ' ': text = ' *' + text[1:]
                else:              text = '*' + text

                if text[-1] == ' ': text = text[:-1] + '* '
                else:               text = text + '*'
                
                subcode.insert_before(text)
            
            subcode.clear()
            subcode.unwrap()


    def procDivWell(self, code):
        while True:
            subcode = code.select_one(self.sanitize('div.well'))
            if not subcode: break

            text = self.processBBcodeChildren(subcode.children)
            if text: subcode.insert_before('\n\n' + text)

            subcode.clear()
            subcode.unwrap()



    # TODO: Threads to fix:

    #   627820 - [Med PRIORITY] Broken link formatting. Happens when an URL link is embedded with img
    #   627663 - [Med PRIORITY] User links need osu.ppy.sh appended
    #   627323 - [Med PRIORITY] Bad formatting first post
    #   627315 - [Med PRIORITY] Bad formatting
    #   627184 - [Med PRIORITY] Bad spacing (excessive spacing)
    #   627168 - [Med PRIORITY] Bad spacing (lacking spacing)
    #   627140 - [Med PRIORITY] Broken link formatting. Happens when an URL link is embedded with img
    #   626945 - [Med PRIORITY] Misc Formatting with notices
    #   626710 - [Med PRIORITY] Collapsed text spoiler shows

    #   628675 - [LOW PRIORITY] Useless space in the end
    #   628627 - [LOW PRIORITY] formatting got split up
    #   628584 - [LOW PRIORITY] Bad text formatting at the end (stray asterisks)
    #   628112 - [LOW PRIORITY] Bad text formatting at the end (stray asterisks)
    #   627663 - [LOW PRIORITY] Figure out how to handle same line images better
    #   627630 - [LOW PRIORITY] Awkward break off at bottom
    #   627244 - [LOW PRIORITY] Spoiler box formatting
    #   627136 - [LOW PRIORITY] Useless space in the beggining one of the split up posts
    #   627081 - [LOW PRIORITY] Figure out how to handle same line images better
    #   626918 - [LOW PRIORITY] Figure out how to handle same line images better
    #   626879 - [LOW PRIORITY] Figure out how to handle same line images better
    #   626854 - [LOW PRIORITY] Useless space post
    #   626816 - [LOW PRIORITY] Rogue asterisks


    # TODO: Posts to fix:

    #   6204742 - [Med PRIORITY] Uneeded line breaks