def bridge_method(func):
    """ decorator to assist with bridging methods """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AttributeError as e:
            print("Implementation Error: {0}".format(e))

    return wrapper
