# Below is what will be displayed in Domoticz GUI under HW
#
"""
<plugin key="Roku" name="Roku (like Kodi)" author="wyn" version="1.0.0">
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="40px" required="true" default="8060"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="True" />
            </options>
        </param>
    </params>
</plugin>
"""
#
# Main Import
import Domoticz
import os
import sys

sys.path.append(os.path.dirname(os.__file__) + '/dist-packages')

import roku

COMMANDS = {
    'Rewind': 'reverse',
    'FastForward': 'forward',
    'Back': 'backspace',
    'Mute':'volumemute'
}

class RokuPlugin:
    enabled = False
    def __init__(self):
        self.isConnected = False
        self.config = {}
        self.r = None

    def onStart(self):
        Domoticz.Log("onStart called")

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        if (len(Devices) == 0):
            Domoticz.Device(Name="Status", Unit=1, Type=17, Image=2, Switchtype=17).Create()
            Domoticz.Log("Devices created.")

        DumpConfigToLog()
        Domoticz.Heartbeat(20)

        self.config = {
            "description":  "Domoticz"              ,
            "host"       :  Parameters["Address"]   ,
            "port"       :  int(Parameters["Port"])
        }

        Domoticz.Log("Connecting to: " + Parameters["Address"] + ":" + Parameters["Port"])

        try:
            self.r = roku.Roku(self.config['host'])
            self.isConnected = True
            Devices[1].Update(nValue=1, sValue='Roku')
        except Exception as e:
            if (self.isConnected == True):
                if Parameters["Mode6"] == "Debug":
                    Domoticz.Log("Devices are connected - Initialisation")
            else:
                Domoticz.Error("Failed to connect: " + e)

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")
        if (Status == 0):
            self.r = roku.Roku(self.config['host'])
            self.isConnected = True
            Domoticz.Log("Connected successfully")

    def onMessage(self, Connection, Data, Status, Extra):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

        Command = Command.strip()
        action, sep, params = Command.partition(' ')
        action = action.capitalize()

        if (self.isConnected == True):
            if (Unit == 1):
                self.send(action, Unit, Level)
            else:
                Domoticz.Error('Unknown key...!!! ???')

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")
        self.isConnected = False

    def onHeartbeat(self):
        pass

    # Update Device into DB
    def updateDevice(self, Unit, nValue, sValue):
        # Make sure that the Domoticz device still exists (they can be deleted) before updating it
        if (Unit in Devices):
            if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
                Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
                Domoticz.Log("Update " + str(nValue) + ":'" + str(sValue) + "' (" + Devices[Unit].Name + ")")

    # Send the command to Samsung TV and update data
    def send(self, KEY, Unit, Level):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Log("Send key : %s " % KEY)

        if KEY in COMMANDS:
            func = getattr(self.r, COMMANDS[KEY])
        else:
            func = getattr(self.r, KEY.lower())
        func()

global _plugin
_plugin = RokuPlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Connection, Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect():
    global _plugin
    _plugin.onDisconnect()

def onHeartbeat(Connection):
    global _plugin
    _plugin.onHeartbeat(Connection)

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
