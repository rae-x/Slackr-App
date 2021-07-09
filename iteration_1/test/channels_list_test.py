import pytest
from error import InputError 
from auth import auth_register
from channels import channels_list,channels_create
from channel import channel_join,channel_leave

@pytest.fixture 
def get_new_user():
    data = auth_register("haydensmith@unsw.edu.au","123456","Hayden","Smith")
    return (data['token'])

#This function checks for user not in any channel
def test_channels_list_empty(get_new_user):
    token = get_new_user
    assert channels_list(token) == {'channels': []}

#This function checks for user in 1 non_public channel
def test_channels_list_nonpublic(get_new_user):
    token = get_new_user

    #Get the channel id for the first channel
    first_channelid = channels_create(token,'First channel',False)

    #Put user into the first channel. 
    channel_join(token,first_channelid)
    
    #Check that channel list prints out the correct data
    assert channels_list(token) == {'channels':[{ 'channel_id': 1, 'name': 'First channel'}]}

#This function checks for user in 1 public channel
def test_channels_list_public(get_new_user):
    token = get_new_user

    #Get the channel id for the first channel, which is public
    first_channelid = channels_create(token,'First channel',True)

    #Put user1 into the first channel. 
    channel_join(token,first_channelid)

    #Check that channel list prints out the correct data
    assert channels_list(token) == {'channels':[{ 'channel_id': 1, 'name': 'First channel'}]}

#This function checks for user in a few channels, and not in some. 
def test_channels_list_multiple(get_new_user):
    token = get_new_user

    #Get the channel id for the first and second channel, which is public
    first_channelid = channels_create(token,'First channel',True)
    second_channelid = channels_create(token,'Second channel',True)

    #Third and fourth channels are created, but the user is not joined. 
    channels_create(token,'Third channel',True)
    channels_create(token,'Fourth channel',True)

    #Put user1 into the first and second channel. 
    channel_join(token,first_channelid)
    channel_join(token,second_channelid)

    #Check that channel list prints out the correct data
    assert channels_list(token) == {'channels':[{ 'channel_id': 1, 'name': 'First channel'},
    {'channel_id': 1, 'name': 'Second channel'}]}

#This function tests for when the user joins a channel, then leave it. 
def test_channels_list_leave(get_new_user):
    token = get_new_user

    #Get the channel id for the first and second channels
    first_channelid = channels_create(token,'First channel',True)
    second_channelid = channels_create(token,'Second channel',True)

    #Put user into the first and second channel. 
    channel_join(token,first_channelid)
    channel_join(token,second_channelid)

    #Make the user leave the second channel
    channel_leave(token,second_channelid)

    #Check that channel list prints out the correct data, which is only first channel
    assert channels_list(token) == {'channels':[{ 'channel_id': 1, 'name': 'First channel'}]}