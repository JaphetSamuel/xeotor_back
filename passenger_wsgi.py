import os
import sys
from main import app
from a2wsgi import ASGIMiddleware

print("quelqque chose")

application = ASGIMiddleware(app)


sys.path.insert(0, os.path.dirname(__file__))
