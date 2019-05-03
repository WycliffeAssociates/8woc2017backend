class Downloads(object):
    def __init__(self, **kwargs):
        for field in (
                'filename'):
            setattr(self, field, kwargs.get(field, None))
