#!/usr/bin/env python
"""
user.py - Gazelle User Module
Copyright 2013 AzzA/Mochaka etc.
Licensed under My Dick.
"""

# TODO delete unused imports
#import json
#import string
import locale
locale.setlocale(locale.LC_ALL, 'en_US.utf8')

def user(phenny, inp):
    """ Gives user stats and information from the site."""
    etx = '\x03'
    if not inp.group(2):
        user_name = inp.nick
    else:
        user_name = inp.group(2).strip()
    i = phenny.callGazelleApi({'username': user_name, 'action': 'userInfo'})
    print(i)

    try:
        # Username
        o = etx + '10[ ' + etx + '07' + i['username']
    except KeyError:
        phenny.say(etx + '10[' + etx + '07 User Not Found ' + etx + '10]')
        return ""

    # Donor
    if int(i['enable']) == 1 and int(i['donor']) == 1:
        o += ' ' + etx + '4<3'
    elif int(i['donor']) == 1:
        o += ' ' + etx + '4</3'

    o += ' ' + etx + '10] :: '

    # Class
    o += '[ ' + etx + '3Class: ' + etx + '07' + i['class'] + ' ' + etx + '10] :: '

    # Ratio and Stats, depending on paranoia
    if int(i['paranoia']) < 4:
        o += '[ ' + etx + '3Up: ' + etx + '07' + i['upload'] + ' ' + etx + '12| ' + etx + '3Down: ' + etx + '07' + i['download'] + ' ' + etx + '12| ' + etx + '3Ratio: ' + etx + '07' + i['ratio'] + ' ' + etx + '10] :: '
        # Gold
        o += '[ ' + etx + '3Gold: ' + etx + '07' + i['gold'] + ' ' + etx + '10] :: '

    # Is the user enabled
    if int(i['enable']) == 1:
        o += '[ ' + etx + '3Enabled: ' + etx + '9Yes ' + etx + '10] :: '
    else:
        o += '[ ' + etx + '3Enabled: ' + etx + '4No ' + etx + '10] :: '

    # When was the user last seen
    if int(i['paranoia']) < 5:
        o += '[ ' + etx + '3Last Seen: ' + etx + '07' + i['lastseen'] + ' ' + etx + '10] :: '

    o += etx + '10[ ' + etx + '3Line Count:' + etx + '07 ' + locale.format('%d', int(i['linecount']), 1) + ' ' + etx + '10] :: '
    """
    # Build the irc bonus tag
    o += '[ '
    if int(i['bonusdisabled']) == 1:
        o += etx + '3IRC Bonus: ' + etx + '4No [Disabled]'
    elif int(i['bonusdisabled']) != 1 and int(i['online']) == 1:
        o += etx + '3IRC Bonus: ' + etx + '9Yes'
    elif int(i['online']) == 2:
        o += etx + '3IRC Bonus: ' + etx + '7No [AFK]'
    else:
        o += etx + '3IRC Bonus: ' + etx + '4No [Offline]'
    o += ' ' + etx + '10] :: '
    """
    o += '[ {0}3Profile: {0}07https://{1}/user.php?id={2} {0}10]'.format(
        etx,
        phenny.config.gazelle_url,
        i['userid'])

    phenny.say(o)

user.commands = ['u', 'user']
user.priority = 'high'
user.example = '!u Daedy'

def tip(phenny, inp):
    """ For tipping a user on site with gold."""

    args = inp.group(0).split()
    args.pop(0)

    totip = args[0]
    amount = args[1]

    if not amount.isdigit():
        phenny.say('To tip a user use the command !tip user amount')
    elif int(amount) <= 0:
        phenny.say('You tried to tip an invalid amount.')
    else:
        i = phenny.callGazelleApi({'userid': inp.uid,
                                   'mod': inp.mod,
                                   'totip': totip,
                                   'amount': amount,
                                   'action': 'tipUser'})
        if not i or i['status'] == "error":
            phenny.say(i['error'])
        else:
            phenny.say(i['msg'])
tip.commands = ['tip']
tip.example = '!tip Daedy 10'

if __name__ == '__main__':
    print(__doc__)
