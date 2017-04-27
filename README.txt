Installation &c.

1) Run ./phenny - this creates a default config file
2) Edit ~/.config/default.py
3) Run ./phenny - this now runs phenny with your settings

Enjoy!

-- 
To add new casino modules, place the main supporting module in casino/. 
This will have the games main functionality and tie into the cards and player modules.
Next place a second module for the game in modules/gazelle/ that contains the IRC commands
and link it back to the main game module in casino/.
