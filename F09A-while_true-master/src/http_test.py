"""
Helper functions used by some HTTP testing files
"""

import requests
from error import InputError, AccessError

PORT = "8080"
APP_URL = "http://127.0.0.1:" + PORT

def process(data):
    """
    If a field in the input dictionary contains None,
    remove it from the dictionary. This is used so
    that test functions can put None into the input
    data, and see how the HTTP server responds to
    that property of the input URL args / POST data
    being missing entirely.
    """
    if data is not None:
        return {key: value for key, value in data.items() if value is not None}
    return data

def handle(data):
    """
    Converts HTTP errors returned by requests into
    either an InputError or an AccessError
    """
    if "code" in data and data["code"] == 400:
        if "Input error" in data["message"]:
            raise InputError(description=data["message"])
        if "Access error" in data["message"]:
            raise AccessError(description=data["message"])
    return data

def get(path, data=None):
    """Make a GET request"""
    return handle(requests.get(APP_URL + "/" + path, params=process(data)).json())

def post(path, data=None):
    """Make a POST request"""
    return handle(requests.post(APP_URL + "/" + path, json=process(data)).json())

def put(path, data=None):
    """Make a PUT request"""
    return handle(requests.put(APP_URL + "/" + path, json=process(data)).json())
