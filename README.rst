domoticz_skill
==============

|Licence| |Code Health| |Coverage Status|

+------------------+--------------------+
| Status           | Operating system   |
+==================+====================+
| |Build Status|   | Linux x86\_64      |
+------------------+--------------------+

This skill is for controlling Domoticz with the source voice assistant Mycroft.


Requirements
------------

-  `Python3`_.
-  `Domoticz`_.
-  `Mycroft`_.


Configuration
-------------

Name your devices in Domoticz like this: "Where What".  Mycroft will look for the device listed
in Domoticz. However the skill will also look for "What Where" as well.  Devices can also be
referenced by "What" alone but Mycroft will only fall back to that if it can't find the device
using "Where What" or "What Where".

Note:  Especially with weather sensors try to name your devices something that won't interfere
with other skills.  For instance naming a device "weather" could cause Mycroft to give you the
current stat for the device named "weather" if you ask "what's the weather" rather than telling
you what the current weather is via the weather skill.

If you add or change the name for a device or scene in Domoticz, then you must reload mycroft
to pick up the new names.

Domoticz Groups and Scenes
-----

If you want Mycroft to do things like "turn off all the lights" in Domoticz then make a
scene or group named "all the lights" with all the lights in it and the skill will find this
group and operate the whole group rather than an individual object.  One caveat is that you
want to make the scene name distinct from the individual switch name.  Mycroft is not good
at picking out the "S" sound at the end of the word.  So a group with items in it called
Kitchen Light, Counter Light and Stove Light, won't work properly if you call the groups
name "Kitchen Lights".  Mycroft will trigger on "Kitchen Light" before it triggers on
"Kitchen Lights".  So if you say "Hey Mycroft turn off the kicthen lights" it will most
likely only turn off the light named "Kitchen Light".

Mycroft Settings Page
-----

The default settings for the domoticz connection and configuration is the local host without
authentication.  

Usage
-----

In English :

Examples of Domoticz device names:

-  outside temperature
-  outside light
-  front door lock
-  mantle
-  reading
-  one
-  two
-  bedroom
-  kitchen light one
-  kitchen light two

Examples Domoticz scene or group names:

-  movie
-  romantic
-  living room  
-  everything
-  bed time

Domoticz scenes: contain a mix devices that can be "on" OR "off".  Scenes have a single button to set the scene.
Domoticz groups: contain devices that toggle on/off together as a group.  Groups have two buttons: on and off.


example phrases:

-  Hey Mycroft turn on the living room lights
-  Hey Mycroft turn on bedroom light
-  Hey Mycroft turn on movie lighting 
-  Hey Mycroft what is the outside temperature?
-  Hey Mycroft lock the front door
-  Hey Mycroft dim the dining room lights by 50%
-  Hey Mycroft set dining room light to 75%
-  Hey Mycroft set the mantle light to red

NOTES:
-  dimmer values have only 20 steps to choose from counting by 5.  e.g. 5% 10% 15%...  Use "set" to jump. "dim" or "brighten" to increase/decrease from current level.
-  color names are in english only. There are 170 colors to choose from and their names can be found in colors.cfg or vocab/en-us/ColorKeyword.voc 

In French (not yet tested) :

-  allume la lumière du salon
-  éteind la lumiere du salon


Todo
----

-  Use with Tasker on Android for send command voice to Mycroft.
-  Color names need a translator


.. _Python3: https://www.python.org/downloads/
.. _Mycroft: https://mycroft.ai/
.. _Domoticz: https://domoticz.com/


.. |Licence| image:: https://img.shields.io/packagist/l/doctrine/orm.svg
.. |Code Health| image:: https://landscape.io/github/matleses/domoticz_skill/master/landscape.svg?style=flat
   :target: https://landscape.io/github/matleses/domoticz_skill/master
.. |Coverage Status| image:: https://coveralls.io/repos/github/matleses/domoticz_skill/badge.svg?branch=master
   :target: https://coveralls.io/github/matleses/domoticz_skill?branch=master
.. |Build Status| image:: https://travis-ci.org/matleses/domoticz_skill.svg?branch=master
   :target: https://travis-ci.org/matleses/domoticz_skill
