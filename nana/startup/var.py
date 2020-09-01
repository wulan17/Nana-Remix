from os import environ

def get_var(name, default=None):
    ENV = bool(environ.get('ENV', False))
    if ENV:
        return environ.get(name, default)
    else:
        from nana.config import Development as Config
        try:
            return getattr(Config, name)
        except AttributeError:
            return None