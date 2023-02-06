import asyncio
import time
import random
import pandas as pd
import configparser
from config import api_id, api_hash, phone, key_words

from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import PeerFloodError, SessionPasswordNeededError
config = configparser.ConfigParser()
config.read('config.ini')

client = TelegramClient(phone, api_id, api_hash)
client.connect()

if not client.is_user_authorized():
    # request one time code
    client.send_code_request(phone)
    try:
        client.sign_in(phone, input('Enter verification code: '))
    # additional code for authorization
    except SessionPasswordNeededError:
        client.sign_in(password=input("Enter password: "))


def parse_channels():
    channels = [dialog for dialog in client.get_dialogs() if dialog.is_channel]
    # create data frames
    d = {'Channels': [str(i.title) for i in channels]}
    df = pd.DataFrame(data=d)
    # convert data frames to html tables
    html = df.to_html()
    text_file = open('channels.html', "w")
    text_file.write(html)
    print('From which channel you want to parse members:')
    # list of channels 
    print('Channels')
    print('--------')
    [print(str(channels.index(i)) + ' - ' + i.title) for i in channels]
    channel_index = input("Enter channel number: ")
    return channels[int(channel_index)]


def parse_chats():
    chats = [dialog for dialog in client.get_dialogs() if dialog.is_group]
    # create data frames
    d = {'Chats': [str(i.title) for i in chats]}
    df = pd.DataFrame(data=d)
    # convert data frames to html tables
    html = df.to_html()
    text_file = open('chats.html', "w")
    text_file.write(html)
    print('From which chat you want to parse members:')
    # list of chats
    print('Chats')
    print('-----')
    [print(str(chats.index(i) + 1) + ' - ' + i.title) for i in chats]
    chat_index = input("Enter chat number: ")
    return chats[int(chat_index)] 

# get users from chats and channels
def get_users(channel):
    users = client.get_participants(channel) 
    df3 = pd.DataFrame(columns=['username', 'name', 'group'])
    for user in users:
        if user.username:
            username = user.username
        else:
            username = ""
        if user.first_name:
            first_name = user.first_name
        else:
            first_name = ""
        if user.last_name:
            last_name = user.last_name
        else:
            last_name = ""
        name = (first_name + ' ' + last_name).strip()
        df_user = {'username': username, 'name': name, 'group': channel}
        df3 = df3.append(df_user, ignore_index=True)

    html3 = df3.to_html()
    text_file1 = open('users.html', 'w')
    text_file1.write(html3)
    return df3.size

# parse messages on key words
def parse_messages(input_channel):
    all_messages = []
    channel = client.get_entity(input_channel)
    messages = client.get_messages(channel, limit=2)

    for x in messages:
        for word in key_words:
            if word in x.text:
                all_messages.append(x.text) 
    return all_messages
            

if __name__ == '__main__':
    parse_messages(parse_channels())
    get_users(parse_chats())
