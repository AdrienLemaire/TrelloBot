=========
TrelloBot
=========


How to install
--------------

    git clone git+https://github.com/Fandekasp/TrelloBot.git#egg=TrelloBot

    cd TrelloBot

    vim local_settings.py  # and add your settings

    ./ticketbot.py


Settings available
------------------


 * ORGANIZATION = 'Name of your organization'
 * CHANNELS = ['list of', 'channels', 'to connect']
 * NICKSERV_PASS = 'Your registered bot password'
 * TRELLO_API_KEY = 'trello key'
 * TRELLO_TOKEN = 'trello secret token'
 * BOARDS = {'irc_cool_name': 'board_id', }
