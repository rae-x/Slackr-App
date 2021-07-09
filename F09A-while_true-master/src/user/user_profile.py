'''
implementations for user_profile functions
'''
#pylint: disable=invalid-name, line-too-long, len-as-condition, inconsistent-return-statements, too-many-boolean-expressions, too-many-arguments, unexpected-keyword-arg
### Builtin/pip Modules ###
from json import dumps
from io import BytesIO
from flask import request, Blueprint, send_from_directory
from PIL import Image
import requests

### Package Modules ###
from error import InputError, AccessError
from auth import email_valid
from data_store import database

### Page Blueprint ###
USERPROFILE_PAGE = Blueprint("user_page", __name__)

### Routes ###

@USERPROFILE_PAGE.route("/user/profile", methods=['GET'])
def route_user_profile():
    '''
    routes for user_profile
    '''
    u_id = int(request.args.get('u_id'))
    token = request.args.get('token')
    return dumps(user_profile(token, u_id))

@USERPROFILE_PAGE.route("/user/profile/setname", methods=['PUT'])
def route_user_profile_setname():
    '''
    routes for user_profile_setname
    '''
    token = request.json.get('token')
    firstname = request.json.get('name_first')
    lastname = request.json.get('name_last')
    return dumps(user_profile_setname(token, firstname, lastname))

@USERPROFILE_PAGE.route("/user/profile/setemail", methods=['PUT'])
def route_user_profile_setemail():
    '''
    route for user_profile_setemail
    '''
    token = request.json.get('token')
    email = request.json.get('email')
    return dumps(user_profile_setemail(token, email))

@USERPROFILE_PAGE.route("/user/profile/sethandle", methods=['PUT'])
def route_user_profile_sethandle():
    '''
    route for user_profile_sethandle
    '''
    token = request.json.get('token')
    handlestr = str(request.json.get('handle_str'))
    return dumps(user_profile_sethandle(token, handlestr))

@USERPROFILE_PAGE.route('/user/profile/uploadphoto', methods=['POST'])
def route_user_profile_uploadphoto():
    '''
    Route for user_profile_uploadphoto
    '''

    print('Hello there')

    payload = request.json
    token = payload.get('token')
    img_url = payload.get('img_url')
    x_start = int(payload.get('x_start'))
    y_start = int(payload.get('y_start'))
    x_end = int(payload.get('x_end'))
    y_end = int(payload.get('y_end'))

    return dumps(user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end))

@USERPROFILE_PAGE.route('/imgurl', methods=['GET'])
def route_imgurl():
    '''
    Route to get the user profile image url
    '''

    u_id = request.args.get('u_id')

    return send_from_directory('../ProfilePics/', f'{u_id}profileImg.jpg')


### Functions ###

def user_profile(token, u_id):
    '''
    This function returns user, for a valid userid

    Arguments:
        token (string)    - Token of the authorised user
        u_id (int)        - User ID of the user profile

    Exceptions:
        InputError  - Occurs when the user with u_id is not a valid user

    Return Value:
        Returns user, a dictionary containing u_id, email, name_first, name_last, handle_str, profile_img_url on success
    '''

    database.get_authed_user(token)

    if u_id != 0:
        user = database.get_user(u_id)
        return {
            'user':{'u_id': u_id,
                    'email': user.email,
                    'name_first': user.name_first,
                    'name_last': user.name_last,
                    'handle_str': user.handle,
                    'profile_img_url': user.profile_img_url}
        }

    return {
        'user':{'u_id': u_id,
                'email': "hangman@slackr.com.au",
                'name_first': "Hangman",
                'name_last': "Bot",
                'handle_str': "hangman",
                'profile_img_url': "https://visualpharm.com/assets/825/Bot-595b40b65ba036ed117d3818.svg"}
    }

def user_profile_setname(token, name_first, name_last):
    '''
    Changes the name of the authorised user

    Arguments:
        token (string)          - Token of the authorised user
        name_first (string)     - New first name to be set for the authorised user
        name_last (string)      - New last name to be set for the authorised user

    Exceptions:
        InputError  - Occurs when name_first or/and name_last is not bettwen 1 to 50 characters

    Return Value:
        Returns {} on success
    '''
    user = database.get_authed_user(token)

    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description="Name_first must be between 1 to 50 characters")
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description="Name_last must be between 1 to 50 characters")

    user.name_first = name_first
    user.name_last = name_last
    database.update()

    return {
        'user' :{
            'u_id':user.user_id,
            'name_first':user.name_first,
            'name_last':user.name_last,
            'email':user.email,
            'handle_str':user.handle,
            'profile_img_url':user.profile_img_url}
    }

def user_profile_setemail(token, email):
    '''
    Changes the email of the authorised user

    Arguments:
        token (string)          - Token of the authorised user
        email (string)          - New email the authorised user change to

    Exceptions:
        InputError  - Occurs when the email is not valid
                    - Email address already used by another user

    Return Value:
        Returns {} on success
    '''
    user = database.get_authed_user(token)

    if not email_valid(email):
        raise InputError(description="Email is not valid")

    if database.email_in_use(email):
        raise InputError(description="Email address already used by another user")

    user.email = email

    database.update()

    return {'user' :{
        'u_id':user.user_id,
        'name_first':user.name_first,
        'name_last':user.name_last,
        'email':user.email,
        'handle_str':user.handle,
        'profile_img_url':user.profile_img_url}
           }

def user_profile_sethandle(token, handle_str):
    '''
    Changes the handle of the authorised user

    Arguments:
        token (string)          - Token of the authorised user
        handle_str (string)     - Updated handle str of the authorised user

    Exceptions:
        InputError  - Occurs when the length of handle is not between 2 to 20 characters
                    - Handle already taken by another user

    Return Value:
        Returns {} on success
    '''
    user = database.get_authed_user(token)

    if len(handle_str) < 2 or len(handle_str) > 20:
        raise InputError(description="The length of handle must be between 2 to 20 characters")

    if database.handle_in_use(handle_str):
        raise InputError(description="Handle already taken by another user")

    user.set_handle(handle_str)
    database.update()

    return {'user' :{
        'u_id':user.user_id,
        'name_first':user.name_first,
        'name_last':user.name_last,
        'email':user.email,
        'handle_str':handle_str,
        'profile_img_url':user.profile_img_url}
           }

def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Upload a profile photo and crop for the authorised user

    Arguments:
        token (string)          - Token of the authorised user
        img_url (string)        - URL of the image
        x_start (int)           - Start of the x-axis for cropping the image
        y_start (int)           - Start of the y-axis for cropping the image
        x_end (int)             - End of the x-axis for cropping the image
        y_end (int)             - End of the y-axis for cropping the image

    Exceptions:
        InputError  - Occurs when img_url returns an HTTP status other than 200
                    - X_start, y_start, x_end, y_end are not within the dimensions of the image
                    - Image uploaded is not a JPG

    Return Value:
        Returns {} on success
    '''
    PATH = 'ProfilePics/'
    BOX = (x_start, y_start, x_end, y_end)

    if token not in database.active_tokens:
        raise AccessError('Unauthorised User')

    if not img_url.endswith('.jpg') and not img_url.endswith('.jpeg'):
        raise InputError('Image must be of .jpg format')

    FILENAME = str(database.active_tokens[token]) + 'profileImg.jpg'
    ROUTE = 'http://127.0.0.1:' + str(database.current_port) + '/imgurl?u_id=' + str(database.active_tokens[token])

    try:
        img_data = requests.get(img_url)
    except:
        raise InputError('The request failed.')

    if img_data.status_code != 200:
        raise InputError('The request failed.')

    # Create, crop and save the image
    image = Image.open(BytesIO(img_data.content))

    width, height = image.size
    if x_start < 0 or \
       y_start < 0 or \
       (x_end - x_start) < 0 or \
       (x_end - x_start) > width or \
       (y_end - y_start) < 0 or \
       (y_end - y_start) > height:
        raise InputError('Dimensions do not fit image size.')

    image = image.crop(BOX)
    image.save(f'{PATH}{FILENAME}')

    # Update the data_store.
    for user in database.users:
        if user.user_id == database.active_tokens[token]:
            user.profile_img_url = ROUTE
            database.update()
            return {}
