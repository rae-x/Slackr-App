"""
Contains search function and its HTTP route
"""

### Builtin/pip Modules ###
from json import dumps
from flask import request, Blueprint

### Package Modules ###
from data_store import database

### Page Blueprint ###
SEARCH_PAGE = Blueprint("search_page", __name__)

### Routes ###

@SEARCH_PAGE.route("/search", methods=["GET"])
def route_search():
    """
    HTTP route for search
    """
    token = request.args.get("token")
    query = request.args.get("query_str")
    return dumps(search(token, query))

### Functions ###

def search(token, query):
    """
    Searches the entire message history for messages matching a given query
    """
    user = database.get_authed_user(token, error=False)
    results = []

    if isinstance(token, str) and isinstance(query, str) and user:
        query = query.lower().strip()
        if query:
            for channel in database.channels:
                channel_messages = channel.json_messages(user)
                results += [message for message in channel_messages \
                                    if match(message["message"], query)]

    return {"messages": results}

### Helper Functions ###

def match(message, query):
    """
    Determines whether a (processed) query
    matches the given message
    """
    return query in message.lower()
