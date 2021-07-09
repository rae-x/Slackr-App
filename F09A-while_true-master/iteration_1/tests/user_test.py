import pytest
from error import InputError 
from user import user_profile,user_profile_setname,user_profile_setemail,user_profile_sethandle
from auth import auth_register



@pytest.fixture 
def get_new_user():
    data = auth_register("haydensmith@unsw.edu.au","123456","Hayden","Smith")
    return (data['token'],data['u_id'])

def test_valid_user_profile(get_new_user):
    '''
    Tests for a valid user input
    '''
    token, u_id = get_new_user
    assert user_profile(token,u_id) == {'u_id': u_id,'email': 'haydensmith@unsw.edu.au','name_first':'Hayden','name_last':'Smith','handle_str': 'haydensmith'}

def test_invalid_uid_user_profile(get_new_user):
    '''
    Tests for an invalid user input, in which the u_id is invalid
    '''
    invalid_uid = 'randominvaliduid'
    token, u_id = get_new_user
    with pytest.raises(InputError):
        user_profile(token,invalid_uid)

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def test_user_profile_setname_valid(get_new_user):
    '''
    Test for when the first and last name is valid 
    '''
    token, u_id = get_new_user
    firstname = 'Bayden'
    lastname = 'Wmith'
    user_profile_setname(token,firstname,lastname) 
    # successful update of first name and last name should be updated in user, but handle is not updated 
    assert user_profile(token,u_id) == {'u_id': u_id,'email': 'haydensmith@unsw.edu.au','name_first':'Bayden','name_last':'Wmith','handle_str': 'haydensmith'}

def test_user_profile_setname_valid2(get_new_user):
    '''
    Test for when setname succeeds multiple times
    '''
    token, u_id = get_new_user
    firstname1 = 'Bayden'
    lastname1 = 'Wmith'
    user_profile_setname(token,firstname1,lastname1) 
    assert user_profile(token,u_id) == {'u_id': u_id,'email': 'haydensmith@unsw.edu.au','name_first':'Bayden','name_last':'Wmith','handle_str': 'haydensmith'}
    firstname2 = 'Hi'
    lastname2 = 'Bye'
    user_profile_setname(token,firstname2,lastname2)
    assert user_profile(token,u_id) == {'u_id': u_id,'email': 'haydensmith@unsw.edu.au','name_first':'Hi','name_last':'Bye','handle_str': 'haydensmith'}

def test_user_profile_setname_firstname(get_new_user):
    '''
    Test for when the firstname exceeds 50 characters, but lastname is valid
    '''
    token, u_id = get_new_user
    firstname = ('a' * 51)
    lastname = 'Wmith'
    with pytest.raises(InputError):
        user_profile_setname(token,firstname,lastname)


def test_user_profile_setname_lastname(get_new_user):
    '''
    Test for when the lastname exceeds 50 characters, but firstname is valid
    '''
    token, u_id = get_new_user
    firstname = 'Bayden'
    lastname = ('a' * 51)
    with pytest.raises(InputError):
        user_profile_setname(token,firstname,lastname)

def test_user_profile_setemail_valid(get_new_user):
    '''
    Test for when setemail succeeds
    '''
    token, u_id = get_new_user
    valid_email = 'haydensmith1@unsw.edu.au'
    user_profile_setemail(token,valid_email)
    #Check user profile to see the updated email in user
    assert user_profile(token,u_id) == {'u_id': u_id,'email': 'haydensmith1@unsw.edu.au','name_first':'Hayden','name_last':'Smith','handle_str': 'haydensmith'}


def test_user_profile_setemail_same(get_new_user):
    '''
    Tests for when the user tries to change email but the email has already been taken 
    '''    
    token, u_id = get_new_user
    same_email = 'haydensmith@unsw.edu.au'
    with pytest.raises(InputError):
        user_profile_setemail(token,same_email) 

def test_user_profile_setemail_invalid1(get_new_user):
    '''
    Tests for when the user tries to change to an invalid email,where @ is not included in the email address
    '''
    token, u_id = get_new_user
    invalid_email = 'hellogmail.com'
    with pytest.raises(InputError):
        user_profile_setemail(token,invalid_email) 

def test_user_profile_setemail_invalid2(get_new_user):
    '''
    Tests for when the user tries to change to an invalid email(. is not included after @)
    '''       
    token, u_id = get_new_user
    invalid_email = 'hello@gmailcom'
    with pytest.raises(InputError):
        user_profile_setemail(token,invalid_email) 

def test_user_profile_setemail_invalid3(get_new_user):
    '''
    Tests for when the user tries to change to an invalid email(the email address starts with an invalid symbol)
    '''
    token, u_id = get_new_user
    invalid_email = '~hello@gmail.com'
    with pytest.raises(InputError):
        user_profile_setemail(token,invalid_email) 

def test_user_profile_setemail_invalid4(get_new_user):
    '''
    Tests for when the user tries to change to an invalid email(the email address contains 2 '.')
    '''        
    token, u_id = get_new_user
    invalid_email = 'hello@gmail..com'
    with pytest.raises(InputError):
        user_profile_setemail(token,invalid_email) 

def test_user_profile_setemail_invalid5(get_new_user):
    '''
    Test for when the user tries to change to an invalid email(the email address ends with an invalid symbol)
    '''        
    token, u_id = get_new_user
    invalid_email = 'hello@gmail.com~'
    with pytest.raises(InputError):
        user_profile_setemail(token,invalid_email) 

def test_user_profile_setemail_invalid6(get_new_user):
    '''
    Test for when the user tries to change to an invalid email(the email address contains an invalid symbol in the middle)
    '''        
    token, u_id = get_new_user
    invalid_email = 'hello~@gmail.com'
    with pytest.raises(InputError):
        user_profile_setemail(token,invalid_email) 

def test_user_profile_sethandle_valid(get_new_user):
    '''
    Test for setting a valid handle
    '''
    token, u_id = get_new_user
    valid_handle = 'baydenswift'
    user_profile_sethandle(token,valid_handle)
    assert user_profile(token,u_id) == {'u_id': u_id,'email': 'haydensmith@unsw.edu.au','name_first':'Hayden','name_last':'Smith','handle_str': 'baydensmith'}

def test_user_profile_sethandle_short(get_new_user):
    '''
    Input error raised when handle is less than 3 characters 
    '''
    token, u_id = get_new_user
    handle = 'h'
    with pytest.raises(InputError):
        user_profile_sethandle(token,handle)

def test_user_profile_sethandle_long(get_new_user):
    '''
    Input error raised when handle is more than 20 characters 
    '''
    token, u_id = get_new_user
    handle = 'h' * 21
    with pytest.raises(InputError):
        user_profile_sethandle(token,handle)


def test_user_profile_sethandle_same(get_new_user):
    '''
    Input error raised when handle is already taken
    '''
    token, u_id = get_new_user
    handle = 'haydensmith'
    with pytest.raises(InputError):
        user_profile_sethandle(token,handle) 