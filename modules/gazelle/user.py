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
        output = '{0}10[ {0}07{1}'.format(etx, i['username'])
    except KeyError:
        phenny.say('{0}10[{0}07 User Not Found {0}10]'.format(etx))
        return

    # Donor
    if int(i['enable']) == 1 and int(i['donor']) == 1:
        output += ' ' + etx + '4<3'
    elif int(i['donor']) == 1:
        output += ' ' + etx + '4</3'

    output += ' ' + etx + '10] :: '

    # Class
    output += '[ ' + etx + '3Class: ' + etx + '07' + i['class'] + ' ' + etx + '10] :: '

    # Ratio and Stats, depending on paranoia
    if {'ratio_stats', 'share_score', 'gold'} - set(i['paranoia']):
        output += '['
        if 'ratio_stats' not in i['paranoia']:
            output += ' {0}3Up: {0}07{1} {0}12| {0}3Down: {0}07{2} {0}12| 3Ratio: {0}07{3}'.format(etx, i['upload'], i['download'], i['ratio'])
        if 'share_score' not in i['paranoia']:
            output += ' {0}12| {0}3SS: {0}07{1}'.format(etx, i['sharescore'])
        if 'gold' not in i['paranoia']:
            o += ' {0}12| {0}3Gold: {0}07{1}'.format(etx, i['gold'])
        output += ' {0}10] :: '

    # Is the user enabled
    if int(i['enable']) == 1:
        output += '[ {0}3Enabled: {0}9Yes {0}10] :: '.format(etx)
    else:
        output += '[ {0}3Enabled: {0}4No {0}10] :: '.format(etx)

    # When was the user last seen
    if 'last_online' not in i['paranoia']:
        output += '[ {0}3Last Seen: {0}07{1} {0}10] :: '.format(etx, i['lastseen'])

    output += '{0}10[ {0}3Line Count:{0}07 {1} {0}10] :: '.format(
        etx,
        locale.format('%d', int(i['linecount']), 1)
    )
    """
    # Build the irc bonus tag
    output += '[ '
    if int(i['bonusdisabled']) == 1:
        output += etx + '3IRC Bonus: ' + etx + '4No [Disabled]'
    elif int(i['bonusdisabled']) != 1 and int(i['online']) == 1:
        output += etx + '3IRC Bonus: ' + etx + '9Yes'
    elif int(i['online']) == 2:
        output += etx + '3IRC Bonus: ' + etx + '7No [AFK]'
    else:
        output += etx + '3IRC Bonus: ' + etx + '4No [Offline]'
    output += ' ' + etx + '10] :: '
    """
    output += '[ {0}3Profile: {0}07https://{1}/user.php?id={2} {0}10]'.format(
        etx,
        phenny.config.gazelle_url,
        i['userid'])

    phenny.say(output)

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
