#!/usr/bin/env python

"""
The card bot for Trello
Inspired from django-cardbot
"""
import sys
import re

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

try:
    #Make a symbolic link name "local_settings.py" with the settings
    from local_settings import *  # NOQA
except ImportError:
    import warnings
    warnings.warn('You should create a local_settings.py')
except Exception as e:
    raise e


card_re = re.compile(r'#(\d+)')
card_url = "https://trello.com/card/1/%s/%s"

board_re = re.compile(r'@(\w+)')
board_url = "https://trello.com/board/1/%s"


class TicketBot(irc.IRCClient):
    """A bot for URLifying Trello boards and cards"""

    nickname = "trellobot"
    password = NICKSERV_PASS
    channels = CHANNELS

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.setNick(self.nickname)
        self.msg('NickServ', 'identify %s' % (self.password))
        for channel in self.channels:
            self.join(channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        cards = card_re.findall(msg)
        boards = board_re.findall(msg)
        if boards:
            board_id = BOARDS[boards[0]]

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            target = user
        else:
            target = channel

        if msg.startswith(self.nickname) and not cards and not boards:
            self.msg(user, "Hi, I'm %s's trellobot I know how to linkify "
                "cards like \"#12345\", and boards like \"r12345\" or "
                "\"[12345]\"." % ORGANIZATION)
            return

        blacklist = range(0, 11)
        for card in set(cards):
            if int(card) in blacklist:
                continue
            self.msg(target, card_url % (board_id, card))
        if not card and board_id:
            self.msg(target, board_url % board_id)
        return


class TicketBotFactory(protocol.ClientFactory):
    """A factory for TicketBots.

    A new protocol instance will be created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = TicketBot

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("connection failed: {}".format(reason))
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)

    # Add variables to environ
    #os.environ['TRELLO_API_KEY'] = TRELLO_API_KEY
    #os.environ['TRELLO_TOKEN'] = TRELLO_TOKEN

    # create factory protocol and application
    f = TicketBotFactory()

    # connect factory to this host and port
    reactor.connectTCP("chat.freenode.net", 6667, f)

    # run bot
    reactor.run()
