import asyncio
import json

import tornado.web
import executor
from cross_origin import CorsHandler


class MainHandler(CorsHandler):
    def post(self):
        # 获取参数
        param = json.loads(self.request.body)
        # 执行代码
        result = executor.execute(param)
        print(result)
        self.write(result)


def make_app():
    return tornado.web.Application([
        (r"/exec", MainHandler),
    ])


async def main():
    app = make_app()
    app.listen(8080)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
