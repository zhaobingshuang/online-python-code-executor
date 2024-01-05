import tornado.web


class CorsHandler(tornado.web.RequestHandler):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.host = ""
    #     self.port = ""
    #
    #     self.set_default_headers()
    #
    # def set_default_headers(self):
    #     super().set_default_headers()
    #
    #     self.set_header("Access-Control-Allow-Origin", "*")
    #     self.set_header("Access-Control-Allow-Credentials", "true")
    #     self.set_header("Access-Control-Allow-Methods", "*")
    #     self.set_header("Access-Control-Allow-Headers", "*")

    def set_default_headers(self):
        origin_url = self.request.headers.get('Origin')
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Credentials", "true")
        # self.set_header("Access-Control-Allow-Headers", "x-requested-with,token")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', '*')
        self.set_header("Access-Control-Max-Age", 1000)
        self.set_header("Content-type", "application/json")

    def options(self):
        self.set_status(200)
        self.finish()
