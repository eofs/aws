class BaseService(object):
    def __init__(self, settings):
        self.settings = settings

    def regions(self, *args, **kwargs):
        raise NotImplementedError('.regions() not implemented.')

    def list(self, *args, **kwargs):
        raise NotImplementedError('.list() not implemented.')