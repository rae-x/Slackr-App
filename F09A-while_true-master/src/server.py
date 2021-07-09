"""
HTTP web server for slackr
"""

import sys
from json import dumps
from flask import Flask
from flask_cors import CORS
from data_store import database
from channel import CHANNEL_PAGE
from channels import CHANNELS_PAGE
from message import MESSAGE_PAGE
from auth import AUTH_PAGE
from users_all import USERS_ALL_PAGE
from user_profile import USERPROFILE_PAGE
from standup import STANDUP_PAGE
from admin_user import ADMIN_USER_PAGE
from workspace_reset import WORKSPACE_RESET_PAGE
from search import SEARCH_PAGE

def default_handler(err):
    """
    This is run when the request matches no route
    """
    response = err.get_response()
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = "application/json"

    return response

APP = Flask(__name__)
CORS(APP)

# Blueprints
for page in (CHANNEL_PAGE,
             CHANNELS_PAGE,
             MESSAGE_PAGE,
             AUTH_PAGE,
             USERS_ALL_PAGE,
             WORKSPACE_RESET_PAGE,
             USERPROFILE_PAGE,
             ADMIN_USER_PAGE,
             STANDUP_PAGE,
             SEARCH_PAGE):
    APP.register_blueprint(page)

APP.config["TRAP_HTTP_EXCEPTIONS"] = True
APP.register_error_handler(Exception, default_handler)

if __name__ == "__main__":
    # Sets up the Data Store
    database.setup()
    PORT = int(sys.argv[1]) if len(sys.argv) == 2 else 8080
    database.current_port = PORT
    APP.run(port=PORT)
