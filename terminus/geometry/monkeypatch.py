# From https://mail.python.org/pipermail/python-dev/2008-January/076194.html

def monkeypatch_method(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator
