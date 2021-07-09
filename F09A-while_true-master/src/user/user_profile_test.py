# pylint: disable=redefined-outer-name, invalid-name, expression-not-assigned, line-too-long
'''
integration tests for user_profile.py
'''
import pytest
from error import InputError, AccessError
from user_profile import user_profile, user_profile_setname, \
                         user_profile_setemail, user_profile_sethandle, \
                         user_profile_uploadphoto
from auth import auth_register
from workspace_reset import workspace_reset

@pytest.fixture(autouse=True)
def call_workspace_reset():
    '''
    Automatic fixture to reset state between tests
    '''
    workspace_reset()

@pytest.fixture
def get_new_user():
    '''
    get the token and uid form auth.register
    '''
    data = auth_register("haydensmith@unsw.edu.au", "123456", "Hayden", "Smith")
    return {"u_id":data['u_id'], "token":data['token']}

def test_valid_user_profile(get_new_user):
    '''
    Tests for a valid user input
    '''
    token = get_new_user["token"]
    u_id = get_new_user["u_id"]
    assert user_profile(token, u_id) == {
        'user':{'u_id': u_id,
                'email': 'haydensmith@unsw.edu.au',
                'name_first':'Hayden',
                'name_last':'Smith',
                'handle_str': 'haydensmith',
                'profile_img_url': 'https://iupac.org/wp-content/uploads/2018/05/default-avatar.png'}
    }

def test_invalid_uid_user_profile(get_new_user):
    '''
    Tests for an invalid user input, in which the u_id is invalid
    '''
    invalid_uid = 'randominvaliduid'
    token = get_new_user["token"]
    with pytest.raises(InputError):
        user_profile(token, invalid_uid)

def test_user_profile_setname_valid(get_new_user):
    '''
    Test for when the first and last name is valid
    '''
    token = get_new_user["token"]
    u_id = get_new_user["u_id"]
    firstname = 'Bayden'
    lastname = 'Wmith'
    user_profile_setname(token, firstname, lastname)
    # successful update of firstname and lastname should be updated in user
    assert user_profile(token, u_id) == {
        'user':{'u_id': u_id,
                'email': 'haydensmith@unsw.edu.au',
                'name_first':'Bayden',
                'name_last':'Wmith',
                'handle_str': 'haydensmith',
                'profile_img_url': 'https://iupac.org/wp-content/uploads/2018/05/default-avatar.png'}
    }

def test_user_profile_setname_valid2(get_new_user):
    '''
    Test for when setname succeeds multiple times
    '''
    token = get_new_user["token"]
    u_id = get_new_user["u_id"]
    firstname1 = 'Bayden'
    lastname1 = 'Wmith'
    user_profile_setname(token, firstname1, lastname1)
    assert user_profile(token, u_id) == {
        'user':{'u_id': u_id,
                'email': 'haydensmith@unsw.edu.au',
                'name_first':'Bayden',
                'name_last':'Wmith',
                'handle_str': 'haydensmith',
                'profile_img_url': 'https://iupac.org/wp-content/uploads/2018/05/default-avatar.png'}
    }
    firstname2 = 'Hi'
    lastname2 = 'Bye'
    user_profile_setname(token, firstname2, lastname2)
    assert user_profile(token, u_id) == {
        'user':{'u_id': u_id,
                'email': 'haydensmith@unsw.edu.au',
                'name_first':'Hi',
                'name_last':'Bye',
                'handle_str': 'haydensmith',
                'profile_img_url': 'https://iupac.org/wp-content/uploads/2018/05/default-avatar.png'}
    }

def test_user_profile_setname_firstname(get_new_user):
    '''
    Test for when the firstname exceeds 50 characters, but lastname is valid
    '''
    token = get_new_user["token"]
    firstname = ('a' * 51)
    lastname = 'Wmith'
    with pytest.raises(InputError):
        user_profile_setname(token, firstname, lastname)


def test_user_profile_setname_lastname(get_new_user):
    '''
    Test for when the lastname exceeds 50 characters, but firstname is valid
    '''
    token = get_new_user["token"]
    firstname = 'Bayden'
    lastname = ('a' * 51)
    with pytest.raises(InputError):
        user_profile_setname(token, firstname, lastname)

def test_user_profile_setemail_valid(get_new_user):
    '''
    Test for when setemail succeeds
    '''
    token = get_new_user["token"]
    u_id = get_new_user["u_id"]
    valid_email = 'haydensmith1@unsw.edu.au'
    user_profile_setemail(token, valid_email)
    #Check user profile to see the updated email in user
    assert user_profile(token, u_id) == {
        'user':{'u_id': u_id,
                'email': 'haydensmith1@unsw.edu.au',
                'name_first':'Hayden',
                'name_last':'Smith',
                'handle_str':'haydensmith',
                'profile_img_url': 'https://iupac.org/wp-content/uploads/2018/05/default-avatar.png'}
    }


def test_user_profile_setemail_same(get_new_user):
    '''
    Tests for when the user tries to change email but the email has already been taken
    '''
    token = get_new_user["token"]
    same_email = 'haydensmith@unsw.edu.au'
    with pytest.raises(InputError):
        user_profile_setemail(token, same_email)

def test_user_profile_setemail_invalid1(get_new_user):
    '''
    Tests for when the user change to an invalid email,where @ is not included in the email address
    '''
    token = get_new_user["token"]
    invalid_email = 'hellogmail.com'
    with pytest.raises(InputError):
        user_profile_setemail(token, invalid_email)

def test_user_profile_setemail_invalid2(get_new_user):
    '''
    Tests for when the user tries to change to an invalid email(. is not included after @)
    '''
    token = get_new_user["token"]
    invalid_email = 'hello@gmailcom'
    with pytest.raises(InputError):
        user_profile_setemail(token, invalid_email)

def test_user_profile_setemail_invalid3(get_new_user):
    '''
    Tests for when the user tries to change to an email address starting with an invalid symbol)
    '''
    token = get_new_user["token"]
    invalid_email = '~hello@gmail.com'
    with pytest.raises(InputError):
        user_profile_setemail(token, invalid_email)

def test_user_profile_setemail_invalid4(get_new_user):
    '''
    Tests for when the user tries to change to an invalid email(the email address contains 2 '.')
    '''
    token = get_new_user["token"]
    invalid_email = 'hello@gmail..com'
    with pytest.raises(InputError):
        user_profile_setemail(token, invalid_email)

def test_user_profile_setemail_invalid5(get_new_user):
    '''
    Test for when the user change to an email address ending with an invalid symbol
    '''
    token = get_new_user["token"]
    invalid_email = 'hello@gmail.com~'
    with pytest.raises(InputError):
        user_profile_setemail(token, invalid_email)

def test_user_profile_setemail_invalid6(get_new_user):
    '''
    Test for when the user change to an email address containing an invalid symbol in the middle
    '''
    token = get_new_user["token"]
    invalid_email = 'hello~@gmail.com'
    with pytest.raises(InputError):
        user_profile_setemail(token, invalid_email)

def test_user_profile_sethandle_valid(get_new_user):
    '''
    Test for setting a valid handle
    '''
    token = get_new_user["token"]
    u_id = get_new_user["u_id"]
    valid_handle = 'baydenswift'
    user_profile_sethandle(token, valid_handle)
    assert user_profile(token, u_id) == {
        'user':{'u_id': u_id,
                'email': 'haydensmith@unsw.edu.au',
                'name_first':'Hayden',
                'name_last':'Smith',
                'handle_str': 'baydenswift',
                'profile_img_url': 'https://iupac.org/wp-content/uploads/2018/05/default-avatar.png'}
    }

def test_user_profile_sethandle_short(get_new_user):
    '''
    Input error raised when handle is less than 2 characters
    '''
    token = get_new_user["token"]
    handle = 'h'
    with pytest.raises(InputError):
        user_profile_sethandle(token, handle)

def test_user_profile_sethandle_long(get_new_user):
    '''
    Input error raised when handle is more than 20 characters
    '''
    token = get_new_user["token"]
    handle = 'h' * 21
    with pytest.raises(InputError):
        user_profile_sethandle(token, handle)


def test_user_profile_sethandle_same(get_new_user):
    '''
    Input error raised when handle is already taken
    '''
    token = get_new_user["token"]
    handle = 'haydensmith'
    with pytest.raises(InputError):
        user_profile_sethandle(token, handle)


def test_user_profile_setimage_valid(get_new_user):
    '''
    Testing successful uploading of profile image.
    '''
    token = get_new_user['token']

    img_url = 'https://library.kissclipart.com/20180904/taq/kissclipart-user-default-clipart-user-default-computer-icons-56aaaf9bba4a6738.jpg'
    SIZE = 500

    assert user_profile_uploadphoto(token, img_url, 0, 0, SIZE, SIZE) == {}

def test_user_profile_setimage_invalidtoken():
    '''
    Uploading a profile image with an invalid token
    '''
    fake_token = -1

    img_url = 'https://library.kissclipart.com/20180904/taq/kissclipart-user-default-clipart-user-default-computer-icons-56aaaf9bba4a6738.jpg'
    SIZE = 500

    with pytest.raises(AccessError) as _:
        user_profile_uploadphoto(fake_token, img_url, 0, 0, SIZE, SIZE) == {}

def test_user_profile_setimage_invalidurl(get_new_user):
    '''
    Uploading a profile image with an invalid url
    '''
    token = get_new_user['token']

    img_url = 'https://doesnotexistcom.au/profile.jpg'
    SIZE = 500

    with pytest.raises(InputError) as _:
        user_profile_uploadphoto(token, img_url, 0, 0, SIZE, SIZE)

def test_user_profile_setimage_invalidformat(get_new_user):
    '''
    Uploading a profile image of format .png instead of .jpg
    '''
    token = get_new_user['token']

    img_url = 'https://cdn.pixabay.com/photo/2017/06/13/12/53/profile-2398782_1280.png'
    SIZE = 500

    with pytest.raises(InputError) as _:
        user_profile_uploadphoto(token, img_url, 0, 0, SIZE, SIZE)

def test_user_profile_setimage_invalid_boundshigher(get_new_user):
    '''
    Uploading a profile image providing higher bounds than image size
    '''
    token = get_new_user['token']

    img_url = 'https://library.kissclipart.com/20180904/taq/kissclipart-user-default-clipart-user-default-computer-icons-56aaaf9bba4a6738.jpg'
    SIZE = 1000

    with pytest.raises(InputError) as _:
        user_profile_uploadphoto(token, img_url, 0, 0, SIZE, SIZE)

def test_user_profile_setimage_invalid_boundslower(get_new_user):
    '''
    Uploading a profile image providing negative bounds
    '''
    token = get_new_user['token']
    img_url = 'https://library.kissclipart.com/20180904/taq/kissclipart-user-default-clipart-user-default-computer-icons-56aaaf9bba4a6738.jpg'
    SIZE = 500

    with pytest.raises(InputError) as _:
        user_profile_uploadphoto(token, img_url, -100, -100, SIZE, SIZE)
