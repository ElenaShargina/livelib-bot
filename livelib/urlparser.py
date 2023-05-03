class Urlparser:
    def __init__(self, prefix=""):
        self.prefix = prefix


    def url_join(self, *args):
        # @todo переименовать массив args
        args = [val for val in args if val]
        last_slash = '/' if args[-1].endswith('/') else ''
        return "/".join(map(lambda x: str(x).strip('/'), args)) + last_slash

    def prefix_join(self,*args):
        return self.url_join(self.prefix, *args)