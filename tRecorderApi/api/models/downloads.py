class Downloads(object):
    def __init__(self, **kwargs):
        for field in ('name','url'):
            setattr(self, field, kwargs.get(field, None))
