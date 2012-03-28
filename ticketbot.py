"""
The card bot for Trello
Inspired from django-cardbot
"""

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

import os
import sys
import re

ORGANIZATION = 'OrganizationName'

card_re = re.compile(r'(?<!build)(?:^|\s)#(\d+)')
card_url = "https://trello.com/card/1/%s/%s"

board_re = re.compile(r'\br(\d+)\b')
board_url = "https://trello.com/board/%s/%s"


class TicketBot(irc.IRCClient):
    """A bot for URLifying Trello boards and cards"""

    nickname = "trellobot"
    password = os.environ['NICKSERV_PASS']
    channels = os.environ['CHANNELS'].split(',')

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
            self.msg(target, card_url % card, board)
        for board in set(boards):
            self.msg(target, board_url % board)
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
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)

    # create factory protocol and application
    f = TicketBotFactory()

    # connect factory to this host and port
    reactor.connectTCP("chat.freenode.net", 6667, f)

    # run bot
    reactor.run()