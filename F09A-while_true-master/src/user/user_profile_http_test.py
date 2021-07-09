# pylint: disable=redefined-outer-name, invalid-name, line-too-long
'''
Tests user_profile routes at the HTTP level
'''
import json
import pytest
import requests
from http_test import APP_URL

### setup ###

@pytest.fixture(autouse=True)
def call_workspace_reset():
    '''
    Automatic fixture to reset state between tests
    '''
    requests.post(APP_URL + "/workspace/reset")

@pytest.fixture
def setup_user():
    '''
    Setups a user and returns a dictionary of the user's ID and token
    '''
    payload = {"email": "johncitizen@hotmail.com",
               "password": "abcdef1",
               "name_first": "John",
               "name_last": "Citizen"}
    response = requests.post(APP_URL + "/auth/register", json=payload)
    data = json.loads(response.text)
    return {"u_id": data["u_id"], "token": data["token"], 'email':payload['email']}

def test_user_profile_invalid_uid(setup_user):
    '''
    tests user_profile when the u_id provided is invalid
    '''
    token = setup_user["token"]
    payload = {"token":token, "u_id":5000}
    response = requests.get(APP_URL + "/user/profile", params=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid user ID" in data["message"]

def test_user_profile_valid_case(setup_user):
    '''
    tests user_profile when input is valid
    '''
    token = setup_user["token"]
    u_id = setup_user["u_id"]
    payload = {"token":token, "u_id":u_id}
    response = requests.get(APP_URL + "/user/profile", params=payload)
    data = json.loads(response.text)
    assert data == {
        'user':
            {'u_id': u_id,
             'email': 'johncitizen@hotmail.com',
             'name_first':'John',
             'name_last':'Citizen',
             'handle_str':'johncitizen',
             'profile_img_url': 'https://iupac.org/wp-content/uploads/2018/05/default-avatar.png'}
    }

def test_user_profile_setname_valid(setup_user):
    '''
    changing the user's name to a valid name
    '''
    token = setup_user["token"]
    u_id = setup_user["u_id"]
    payload = {"token":token, "name_first":"First", "name_last":"Last"}
    response = requests.put(APP_URL + "/user/profile/setname", json=payload)
    data = json.loads(response.text)
    assert data == {
        'user':
            {'u_id': u_id,
             'email': 'johncitizen@hotmail.com',
             'name_first':'First',
             'name_last':'Last',
             'handle_str':'johncitizen',
             'profile_img_url': 'https://iupac.org/wp-content/uploads/2018/05/default-avatar.png'}
    }

def test_user_profile_setname_invalid_first(setup_user):
    '''
    changing the user's name to a invalid firstname
    '''
    token = setup_user["token"]
    invalid_firstname = ('a'*51)
    payload = {"token":token, "name_first":invalid_firstname, "name_last":"Last"}
    response = requests.put(APP_URL + "/user/profile/setname", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 \
        and "Name_first must be between 1 to 50 characters" in data["message"]

def test_user_profile_setname_invalid_last(setup_user):
    '''
    changing the user's name to an invalid lastname
    '''
    token = setup_user["token"]
    invalid_lastname = ('a'*51)
    payload = {"token":token, "name_first":"First", "name_last":invalid_lastname}
    response = requests.put(APP_URL + "/user/profile/setname", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 \
        and "Name_last must be between 1 to 50 characters" in data["message"]

def test_user_profile_setemail_invalid(setup_user):
    '''
    tests changing the email when the email is invalid
    '''
    token = setup_user["token"]
    email = "invalid@email.com!"
    payload = {"token":token, "email":email}
    response = requests.put(APP_URL + "/user/profile/setemail", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "Email is not valid" in data["message"]

def test_user_profile_setemail_same(setup_user):
    '''
    tests changing the email address when the email is already taken
    '''
    token = setup_user["token"]
    email = setup_user["email"]
    payload = {"token":token, "email":email}
    response = requests.put(APP_URL + "/user/profile/setemail", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and \
        "Email address already used by another user" in data["message"]

def test_user_profile_setemail_valid(setup_user):
    '''
    tests when changing to a valid email
    '''
    token = setup_user["token"]
    u_id = setup_user["u_id"]
    payload = {"token":token, "email":"valid@hotmail.com"}
    response = requests.put(APP_URL + "/user/profile/setemail", json=payload)
    data = json.loads(response.text)
    assert data == {
        'user':
            {'u_id': u_id,
             'email': 'valid@hotmail.com',
             'name_first':'John',
             'name_last':'Citizen',
             'handle_str':'johncitizen',
             'profile_img_url': 'https://iupac.org/wp-content/uploads/2018/05/default-avatar.png'}
    }

def test_user_profile_sethandle_valid(setup_user):
    '''
    tests user_profile_sethandle when the handle is valid
    '''
    token = setup_user["token"]
    u_id = setup_user["u_id"]
    payload = {"token":token, "handle_str":"validhandle"}
    requests.put(APP_URL + "/user/profile/sethandle", json=payload)
    payload = {"token": token, "u_id": u_id}
    response = requests.get(APP_URL + "/user/profile", params=payload)
    data = json.loads(response.text)
    assert data == {
        'user':
            {'u_id': u_id,
             'email': 'johncitizen@hotmail.com',
             'name_first':'John',
             'name_last':'Citizen',
             'handle_str':'validhandle',
             'profile_img_url': 'https://iupac.org/wp-content/uploads/2018/05/default-avatar.png'}
    }

def test_user_profile_sethandle_invalid(setup_user):
    '''
    tests user_profile_sethandle when the handle is invalid
    '''
    token = setup_user["token"]
    payload = {"token":token, "handle_str":"a"}
    response = requests.put(APP_URL + "/user/profile/sethandle", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and \
    "The length of handle must be between 2 to 20 characters" in data["message"]

def test_user_profile_sethandle_used(setup_user):
    '''
    tests user_profile_sethandle when the handle is already taken
    '''
    token = setup_user["token"]
    payload = {"token":token, "handle_str":"johncitizen"}
    response = requests.put(APP_URL + "/user/profile/sethandle", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "Handle already taken by another user" in data["message"]

def test_user_profile_setimage_valid(setup_user):
    '''
    Testing successful uploading of profile image.
    '''
    token = setup_user['token']
    img_url = 'https://library.kissclipart.com/20180904/taq/kissclipart-user-default-clipart-user-default-computer-icons-56aaaf9bba4a6738.jpg'
    SIZE = 500

    payload = {'token':token, 'img_url': img_url, 'x_start':0, 'y_start':0, 'x_end': SIZE, 'y_end': SIZE}
    response = requests.post(APP_URL + '/user/profile/uploadphoto', json=payload)
    assert response.status_code == 200

def test_user_profile_setimage_invalidtoken():
    '''
    Uploading a profile image with an invalid token
    '''
    fake_token = -1
    img_url = 'https://library.kissclipart.com/20180904/taq/kissclipart-user-default-clipart-user-default-computer-icons-56aaaf9bba4a6738.jpg'
    SIZE = 500

    payload = {'token':fake_token, 'img_url': img_url, 'x_start':0, 'y_start':0, 'x_end': SIZE, 'y_end': SIZE}
    response = requests.post(APP_URL + '/user/profile/uploadphoto', json=payload)
    data = json.loads(response.text)['message']
    assert response.status_code == 400 and 'Unauthorised User' in data

def test_user_profile_setimage_invalidurl(setup_user):
    '''
    Uploading a profile image with an invalid url
    '''
    token = setup_user['token']
    img_url = 'https://doesnotexistcom.au/profile.jpg'
    SIZE = 500

    payload = {'token':token, 'img_url': img_url, 'x_start':0, 'y_start':0, 'x_end': SIZE, 'y_end': SIZE}
    response = requests.post(APP_URL + '/user/profile/uploadphoto', json=payload)
    data = json.loads(response.text)['message']
    assert response.status_code == 400 and 'The request failed' in data

def test_user_profile_invalidformat(setup_user):
    '''
    Uploading a profile image of format .png instead of .jpg
    '''
    token = setup_user['token']
    img_url = 'https://cdn.pixabay.com/photo/2017/06/13/12/53/profile-2398782_1280.png'
    SIZE = 500

    payload = {'token':token, 'img_url': img_url, 'x_start':0, 'y_start':0, 'x_end': SIZE, 'y_end': SIZE}
    response = requests.post(APP_URL + '/user/profile/uploadphoto', json=payload)
    data = json.loads(response.text)['message']
    assert response.status_code == 400 and 'Image must be of .jpg format' in data

def test_user_profile_setimage_invalid_boundshigher(setup_user):
    '''
    Uploading a profile image providing higher bounds than image size
    '''
    token = setup_user['token']
    img_url = 'https://library.kissclipart.com/20180904/taq/kissclipart-user-default-clipart-user-default-computer-icons-56aaaf9bba4a6738.jpg'
    SIZE = 1000

    payload = {'token':token, 'img_url': img_url, 'x_start':0, 'y_start':0, 'x_end': SIZE, 'y_end': SIZE}
    response = requests.post(APP_URL + '/user/profile/uploadphoto', json=payload)
    data = json.loads(response.text)['message']
    assert response.status_code == 400 and 'Dimensions do not fit image size' in data

def test_user_profile_setimage_invalid_boundslower(setup_user):
    '''
    Uploading a profile image providing negative bounds
    '''
    token = setup_user['token']
    img_url = 'https://library.kissclipart.com/20180904/taq/kissclipart-user-default-clipart-user-default-computer-icons-56aaaf9bba4a6738.jpg'
    SIZE = 500

    payload = {'token':token, 'img_url': img_url, 'x_start':-100, 'y_start':-100, 'x_end': SIZE, 'y_end': SIZE}
    response = requests.post(APP_URL + '/user/profile/uploadphoto', json=payload)
    data = json.loads(response.text)['message']
    assert response.status_code == 400 and 'Dimensions do not fit image size' in data
