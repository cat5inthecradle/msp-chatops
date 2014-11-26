#!/usr/bin/python

# v0.0

#
# This is based on an example JabberBot that serves as broadcasting server.
# Users can subscribe/unsubscribe to messages and send messages 
# by using "broadcast". It also shows how to send message from 
# outside the main loop, so you can inject messages into the bot 
# from other threads or processes, too.
#

from jabberbot import JabberBot, botcmd

import threading
import time 
import logging
import json

with open('config.json') as json_data_file:
    config = json.load(json_data_file)

JID = config["connection"]["jid"]
PASSWORD = config["connection"]["password"]

class RobotJabberBot(JabberBot):
    """This is a simple broadcasting client. Use "subscribe" to subscribe to broadcasts, "unsubscribe" to unsubscribe and "broadcast" + message to send out a broadcast message. Automatic messages will be sent out all 60 seconds."""

    def __init__( self, jid, password, res = None):
        super( RobotJabberBot, self).__init__( jid, password, res)
        # create console handler
        chandler = logging.StreamHandler()
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # add formatter to handler
        chandler.setFormatter(formatter)
        # add handler to logger
        self.log.addHandler(chandler)
        # set level to INFO
        self.log.setLevel(logging.INFO)

        self.users = []
        self.message_queue = []
        self.thread_killed = False

    @botcmd
    def subscribe( self, mess, args):
        """Subscribe to the broadcast list"""
        user = mess.getFrom()
        if user in self.users:
            return 'You are already subscribed.'
        else:
            self.users.append( user)
            self.log.info( '%s subscribed to the broadcast.' % user)
            return 'You are now subscribed.'

    @botcmd
    def unsubscribe( self, mess, args):
        """Unsubscribe from the broadcast list"""
        user = mess.getFrom()
        if not user in self.users:
            return 'You are not subscribed!'
        else:
            self.users.remove( user)
            self.log.info( '%s unsubscribed from the broadcast.' % user)
            return 'You are now unsubscribed.'
    
    @botcmd
    def joke( self, mess, args):
        """Tells you a funny joke"""
        user = mess.getFrom()
        wait_then_say(5, "Because that's what it was programmed to do!")
        return "Why did the chickenbot cross the road?"

    # You can use the "hidden" parameter to hide the
    # command from JabberBot's 'help' list
    @botcmd(hidden=True)
    def broadcast( self, mess, args):
        """Sends out a broadcast, supply message as arguments (e.g. broadcast hello)"""
        self.message_queue.append( 'broadcast: %s (from %s)' % ( args, str(mess.getFrom()), ))
        self.log.info( '%s sent out a message to %d users.' % ( str(mess.getFrom()), len(self.users),))

    def idle_proc( self):
        if not len(self.message_queue):
            return

        # copy the message queue, then empty it
        messages = self.message_queue
        self.message_queue = []

        for message in messages:
            if len(self.users):
                self.log.info('sending "%s" to %d user(s).' % ( message, len(self.users), ))
            for user in self.users:
                self.send( user, message)

    def thread_proc( self):
        while not self.thread_killed:
            self.message_queue.append('this is an automatic message, sent all 60 seconds :)')
            for i in range(60):
                time.sleep( 1)
                if self.thread_killed:
                    return

def wait_then_say( timeout, message):
    for i in range(timeout):
        time.sleep( 1)
        """Yea this doesn't work"""
        return message
    


robot = RobotJabberBot( JID, PASSWORD)

th = threading.Thread( target = robot.thread_proc)
robot.serve_forever( connect_callback = lambda: th.start())
robot.thread_killed = True

