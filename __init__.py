# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from os.path import dirname, abspath, join
import sys
import re
import urllib
import urllib.request
import json
import configparser

__author__ = 'mTreussart'

sys.path.append(abspath(dirname(__file__)))
LOGGER = getLogger(__name__)


class DomoticzSkill(MycroftSkill):

    def __init__(self):
        super(DomoticzSkill, self).__init__(name="DomoticzSkill")

    def initialize(self):
        # Download all device names and service names
        where_keywords = self.where_intent()
        i = 0
        while i < len(where_keywords):
            self.register_vocabulary(where_keywords[i], "DynamicWhereKeyword")
            i += 1
        domoticz_switch_intent = IntentBuilder("SwitchIntent")\
            .optionally("TurnKeyword")\
            .require("StateKeyword")\
            .require("WhatKeyword")\
            .require("DynamicWhereKeyword").build()
        self.register_intent(domoticz_switch_intent,
                             self.handle_domoticz_switch_intent)

        # e.g. set the mantle lights to red
        domoticz_color_intent = IntentBuilder("ColorIntent")\
            .optionally("TurnKeyword")\
            .optionally("WhatKeyword")\
            .require("DynamicWhereKeyword")\
            .require("ColorKeyword").build()
        self.register_intent(domoticz_color_intent,
                             self.handle_domoticz_color_intent)

        domoticz_infos_intent = IntentBuilder("InfosIntent")\
            .require("InfosKeyword")\
            .require("WhatKeyword")\
            .optionally("DynamicWhereKeyword")\
            .optionally("StateKeyword").build()
        self.register_intent(domoticz_infos_intent,
                             self.handle_domoticz_infos_intent)

    def where_intent(self):
        domoticz = Domoticz(
            self.settings.get("hostname"),
            self.settings.get("port"),
            self.settings.get("protocol"),
            self.settings.get("authentication"),
            self.settings.get("username"),
            self.settings.get("password"))
        return domoticz.get_where_names()

    def handle_domoticz_switch_intent(self, message):
        domoticz = Domoticz(
            self.settings.get("hostname"),
            self.settings.get("port"),
            self.settings.get("protocol"),
            self.settings.get("authentication"),
            self.settings.get("username"),
            self.settings.get("password"))
        state = message.data.get("StateKeyword")
        what = message.data.get("WhatKeyword")
        where = message.data.get("DynamicWhereKeyword")
        action = message.data.get("TurnKeyword")
        data = {
            'what': what,
            'where': where
        }

        LOGGER.debug("message : " + str(message.data))
        response = domoticz.switch(state, what, where, action)
        edng = re.compile(str(state).title(), re.I)
        ending = "ed"
        if edng.search('on') or edng.search('off'):
            ending = ""
        if response is None:
            self.speak_dialog("NotFound", data)
        elif response is 0:
            self.speak("The " + str(what) + " is already " + str(state).title() + ending)
        elif response is 1:
            self.speak("The " + str(what) + " can not be operated with " + str(state).title())

    def handle_domoticz_infos_intent(self, message):
        what = message.data.get("WhatKeyword")
        where = message.data.get("DynamicWhereKeyword")
        domoticz = Domoticz(
            self.settings.get("hostname"),
            self.settings.get("port"),
            self.settings.get("protocol"),
            self.settings.get("authentication"),
            self.settings.get("username"),
            self.settings.get("password"))
        data = {
            'what': what,
            'where': where
        }
        response = domoticz.get(what, where)
        data = str(response['Data'])
        if data is None:
            if where is None:
                self.speak_dialog("NotFoundShort", data)
            else:
                self.speak_dialog("NotFound", data)
        if re.search('\d\s+C', data):
            data = data.replace(' C', ' degrees celsius')
        if re.search('\d\s+F', data):
            data = data.replace(' F', ' degrees fahrenheit')
        data = "It's " + data
        LOGGER.debug("result : " + str(data))
        self.speak(str(data))

    def handle_domoticz_color_intent(self, message):
        domoticz = Domoticz(
            self.settings.get("hostname"),
            self.settings.get("port"),
            self.settings.get("protocol"),
            self.settings.get("authentication"),
            self.settings.get("username"),
            self.settings.get("password"))
        what = message.data.get("WhatKeyword")
        if what is None:
            what = "lights"
        where = message.data.get("DynamicWhereKeyword")
        color = message.data.get("ColorKeyword")
        data = {
            'what': what,
            'where': where
        }
        LOGGER.debug("message : " + str(message.data))
        LOGGER.debug("what where color : " + str(what) + " " + str(where) + " " + str(color))
        data = []
        data = domoticz.findid(what, where, None)
        idx = data[0]
        result = data[1]
        stype = data[2]
        dlevel = data[3]
        subtype = data[4]
        switchtype = data[5]
        if result is None:
            self.speak_dialog("NotFound", data)
        elif subtype == "RGB":
            rgb = domoticz.convert_color_to_rgb(color)
            domoticz.set_color(rgb, idx)
        else:
            self.speak("The " + str(where) + " " + str(what) + " is not a color light")

    def stop(self):
        pass


class Domoticz:
    """Class for controlling Domoticz."""
    def __init__(self, host, port, protocol, authentication, login, password):
        """Recover settings for accessing to Domoticz instance."""
        self.host = host
        self.port = port
        protocol = protocol
        authentication = authentication
        if protocol:
            self.protocol = "https"
        else:
            self.protocol = "http"
        if authentication:
            self.login = login
            self.password = password
            self.url = self.protocol + "://" + self.login + ":" + self.password + "@" + self.host + ":" + self.port
        else:
            self.url = self.protocol + "://" + self.host + ":" + self.port

    def get_where_names(self):
        # create array of names for scenes and devices stored in domoticz
        f_scenes = urllib.request.urlopen(self.url + "/json.htm?type=scenes&filter=all&used=true")
        response_scenes = f_scenes.read()
        payload_scenes = json.loads(response_scenes.decode('utf-8'))
        f_devices = urllib.request.urlopen(self.url + "/json.htm?type=devices&filter=all&used=true")
        response_devices = f_devices.read()
        payload_devices = json.loads(response_devices.decode('utf-8'))
        result_array = []
        x = 0
        while x < len(payload_scenes['result']):
            result_array.append(payload_scenes['result'][x]['Name'])
            x += 1
        x = 0
        while x < len(payload_devices['result']):
            result_array.append(payload_devices['result'][x]['Name'])
            x += 1
        return result_array


    def findid(self, what, where, state):
        wht = re.compile(what, re.I)
        whr = re.compile(where, re.I)
        idx = False
        stype = False
        subtype = False
        switchtype = False
        dlevel = False
        result = None
        for rq in [ "devices", "scenes" ]:
            i = 0
            result_search = "Data"
            if rq == "scenes":
                f = urllib.request.urlopen(self.url + "/json.htm?type=scenes&filter=all&used=true")
                result_search = "Status"
            else:
                f = urllib.request.urlopen(self.url + "/json.htm?type=devices&filter=all&used=true")
            response = f.read()
            payload = json.loads(response.decode('utf-8'))
            while i < len(payload['result']):
                if whr.search(payload['result'][i]['Name']):
                    stype = payload['result'][i]['Type']
                    typ = re.compile(stype, re.I)
                    dlevel = "100"
                    if typ.search("Group") or typ.search("Scene"):
                        stype = "scene"
                    elif typ.search("Light/Switch"):
                        stype = "light"
                        dlevel = payload['result'][i]['Level']
                        subtype = payload['result'][i]['SubType']
                        switchtype = payload['result'][i]['SwitchType']
                    elif typ.search("Color Switch"):
                        stype = "light"
                        dlevel = payload['result'][i]['Level']
                        subtype = payload['result'][i]['SubType']
                        switchtype = payload['result'][i]['SwitchType']
                    else:
                        stype = "light"
                    idx = payload['result'][i]['idx']
                    rslt = re.compile(" " + str(state).title(), re.I)
                    if rslt.search(" " + payload['result'][i][result_search]):
                        result = 0
                    else:
                        result = 1
                    break
                elif i is len(payload['result']) - 1:
                    break
                i += 1
        return [idx, result, stype, dlevel, subtype, switchtype]

    def findcmd(self, state, action, dlevel):
        dsrdst = str(state).title()
        act = str(action).title()
        if dsrdst == "None":
            dsrdst = "25%"
        rslt = re.compile(dsrdst, re.I)
        rslt2 = re.compile(act, re.I)
        if dsrdst.find('%') > -1:
            if len(dsrdst) == 3:
                dsrdst = int(dsrdst[0:2])
            elif len(dsrdst) == 4:
                dsrdst = 100
            else:
                dsrdst = 5
        cmd = False
        if rslt2.search('dim') or rslt2.search('decrease'):
            stlvl = int(dlevel) - int(dsrdst)
            if stlvl < 0:
                stlvl = 0
            cmd = "Set%20Level&level=" + str(stlvl)
        elif rslt2.search('brighten') or rslt2.search('increase'):
            stlvl = int(dlevel) + int(dsrdst)
            if stlvl > 100:
                stlvl = 100
            cmd = "Set%20Level&level=" + str(stlvl)
        elif rslt2.search('set'):
            stlvl = int(dsrdst)
            if stlvl > 100:
                stlvl = 100
            elif stlvl < 0:
                stlvl = 0
            cmd = "Set%20Level&level=" + str(stlvl)
        else:
            if rslt.search('lock') or rslt.search('open') or rslt.search('on'):
                cmd = "On"
            elif rslt.search('unlock') or rslt.search('close') or rslt.search('off'):
                cmd = "Off"
        return cmd

    def convert_color_to_rgb(self, color):
        colors_name = "colors.cfg"
        #colors_file = os.path.join(os.path.dirname(__file__), colors_name)
        colors_file = join(dirname(__file__), colors_name)
        self.colors = configparser.ConfigParser()
        self.colors.read(colors_file)
        if color is None:
            return "fff4e5"
        else:
            for (key, val) in self.colors.items("colors"):
                if color.lower().strip() == key.lower().strip():
                    return val
        return "fff4e5"

    def switch(self, state, what, where, action):
        """Switch the device in Domoticz."""
        data = []
        data = self.findid(what, where, state)
        idx = data[0]
        result = data[1]
        stype = data[2]
        dlevel = data[3]
        subtype = data[4]
        switchtype = data[5]
        if result is 1:
            cmd = self.findcmd(state, action, dlevel)
            if cmd:
                try:
                    f = urllib.request.urlopen(self.url + "/json.htm?type=command&param=switch" + stype + "&idx=" + str(idx) + "&switchcmd=" + str(cmd))
                    response = f.read()
                    LOGGER.debug(str(response))
                    return response
                except IOError as e:
                    LOGGER.error(str(e) + ' : ' + str(e.read()))
        else:
            LOGGER.debug("no command found")
        return result

    def get(self, what, where):
        """Get the device's data in Domoticz."""
        try:
            f = urllib.request.urlopen(self.url + "/json.htm?type=devices&filter=all&used=true")
            response = f.read()
            payload = json.loads(response.decode('utf-8'))
            wht = re.compile(what, re.I)
            i = 0
            if where is not None:
                whr = re.compile(where, re.I)
                while i < len(payload['result']):
                    if whr.search(payload['result'][i]['Name']) and whr.search(payload['result'][i]['Name']):
                        break
                    elif i is len(payload['result']) - 1:
                        payload['result'][i]['Data'] = None
                        break
                    i += 1
            elif where is None:
                while i < len(payload['result']):
                    if wht.search(payload['result'][i]['Name']):
                        break
                    elif i is len(payload['result']) - 1:
                        payload['result'][i]['Data'] = None
                        break
                    i += 1
            return payload['result'][i]
        except IOError as e:
            LOGGER.error(str(e) + ' : ' + str(e.read()))

    def set_color(self, rgb, idx):
        """Set the RGB colors in Domoticz."""
        try:
            with urllib.request.urlopen(self.url + "/json.htm?type=command&param=setcolbrightnessvalue&idx=" + str(idx) + "&hex=" + str(rgb) + "&brightness=100&iswhite=false") as url:
                response = url.read()
            LOGGER.debug(str(response))
            return response
        except IOError as e:
            if hasattr(e, 'read'):
                LOGGER.error(str(e) + ' : ' + str(e.read()))
            else:
                LOGGER.error(str(e))

    def setlevel(self, level, idx):
        """Set brightness level in Domoticz."""
        try:
            with urllib.request.urlopen(self.url + "/json.htm?type=command&param=switchlight&idx=" + str(idx) + "&switchcmd=Set%20Level&level=" + str(level)) as url:
                response = url.read()
            LOGGER.debug(str(response))
            return response
        except IOError as e:
            if hasattr(e, 'read'):
                LOGGER.error(str(e) + ' : ' + str(e.read()))
            else:
                LOGGER.error(str(e))

def create_skill():
    return DomoticzSkill()
