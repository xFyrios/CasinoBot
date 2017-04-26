#!/usr/bin/env python
"""
info.py - Phenny Information Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

def commands(phenny, input): 
   '''Returns a list of commands I can undestand'''
   # This function only works in private message
   if input.sender.startswith('#'): return
   names = ', '.join(sorted(phenny.doc.iterkeys()))
   phenny.say('Commands I recognise: ' + names + '.')
   phenny.say("For help, do '!help example' where example is the " + 
               "name of the command you want help for.")
commands.commands = ['commands']
commands.priority = 'low'

def help(phenny, input): 
   '''Gives help in general, or for specific commands'''
   if not input.group(2):
      response = (
         'Hi, I\'m '+ phenny.nick +'! Say "!commands" to me in a PM for a list ' + 
         'of my commands. Or say "!help example" for help with a specific command.'
      )
      phenny.reply(response)
   else:
      name = input.group(2)
      name = name.lower()

      if phenny.doc.has_key(name): 
         phenny.reply(phenny.doc[name][0])
         if phenny.doc[name][1]: 
            phenny.say('e.g. ' + phenny.doc[name][1])
help.commands = ['help']
help.priority = 'low'

def stats(phenny, input): 
   """Show information on command usage patterns."""
   commands = {}
   users = {}
   channels = {}

   ignore = set(['f_note', 'startup', 'message', 'noteuri'])
   for (name, user), count in phenny.stats.items(): 
      if name in ignore: continue
      if not user: continue

      if not user.startswith('#'): 
         try: users[user] += count
         except KeyError: users[user] = count
      else: 
         try: commands[name] += count
         except KeyError: commands[name] = count

         try: channels[user] += count
         except KeyError: channels[user] = count

   comrank = sorted([(b, a) for (a, b) in commands.iteritems()], reverse=True)
   userank = sorted([(b, a) for (a, b) in users.iteritems()], reverse=True)
   charank = sorted([(b, a) for (a, b) in channels.iteritems()], reverse=True)

   # most heavily used commands
   creply = 'most used commands: '
   for count, command in comrank[:10]: 
      creply += '%s (%s), ' % (command, count)
   phenny.say(creply.rstrip(', '))

   # most heavy users
   reply = 'power users: '
   for count, user in userank[:10]: 
      reply += '%s (%s), ' % (user, count)
   phenny.say(reply.rstrip(', '))

   # most heavy channels
   chreply = 'power channels: '
   for count, channel in charank[:3]: 
      chreply += '%s (%s), ' % (channel, count)
   phenny.say(chreply.rstrip(', '))
stats.commands = ['stats']
stats.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()
