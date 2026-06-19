from mangum import Mangum
from love_engine.proxy.proxy_server import app

handler = Mangum(app, lifespan="on")
