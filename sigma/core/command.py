from sigma.core.formatting import code, codeblock

from importlib import reload
from .callable import Callable
from .callable import NotEnabledError


class Command(Callable):
    def __init__(self, plugin, info):
        self.usage = "{pfx:s}{cmd:s}"

        try:
            super().__init__(plugin, info)
        except NotEnabledError:
            return

        self.prefix = self.bot.prefix

    def reload_command(self):
        if self.enabled == True:
            reload(self.module)
        
    def help(self):
        usage = self.usage.format(pfx=self.prefix, cmd=self.name)
        return 'Example: {:s}\n{:s}'.format(
            code(usage), codeblock(self.desc))
