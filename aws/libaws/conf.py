import ConfigParser
import os


class Settings(object):
    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()

        locations = (loc for loc in [os.curdir, os.path.expanduser('~/.aws'), '/etc/aws', os.environ.get('AWS_CONF')] if loc is not None)

        for loc in locations:
            try:
                with open(os.path.join(loc, 'settings.conf')) as source:
                    self.config.readfp(source)
            except IOError:
                pass

    def get(self, section, option, default=None):
        try:
            return self.config.get(section, option)
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError):
            pass
        return default

settings = Settings()