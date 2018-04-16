class Task(object):
    def __init__(self, **kwargs):
        for field in (
                'id',
                'name',
                'current',
                'total',
                'progress',
                'title',
                'message',
                'details',
                'status',
                'started',
                'finished'):
            setattr(self, field, kwargs.get(field, None))
