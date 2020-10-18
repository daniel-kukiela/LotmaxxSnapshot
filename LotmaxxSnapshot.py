# Copyright (c) 2020 DhanOS
# The LotmaxxSnapshot is released under the terms of the AGPLv3 or higher.

import re
import os
from collections import OrderedDict

from UM.Extension import Extension
from UM.Application import Application
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Logger import Logger

from cura.Snapshot import Snapshot


class LotmaxxSnapshot(Extension):
    def __init__(self):
        super().__init__()

        Application.getInstance().getOutputDeviceManager().writeStarted.connect(self.add_snapshot_to_gcode)
        self.scene = Application.getInstance().getController().getScene()

    def create_snapshot(self, size):
        snapshot = Snapshot.snapshot(width=size[0], height=size[1])
        #snapshot.save(os.path.dirname(__file__) + "/test.png")
        gcode = ''
        for y in range(snapshot.height()):
            for x in range(snapshot.width()):
                pixel = snapshot.pixelColor(x, y)
                rgb16 = (pixel.red() >> 3 << 11) | (pixel.green() >> 2 << 5) | (pixel.blue() >> 3)
                rgb16_hex = "{:04x}".format(rgb16)
                rgb16_hex_le = rgb16_hex[2:4] + rgb16_hex[0:2]
                gcode += rgb16_hex_le

            gcode += '\rM10086 ;'
        gcode += '\r'

        return gcode

    def add_snapshot_to_gcode(self, output_device):

        if not hasattr(self.scene, "gcode_dict") or not self.scene.gcode_dict:
            Logger.log("w", "Scene does not contain any gcode")
            return

        for build_plate_number, gcode_list in self.scene.gcode_dict.items():
            for index, gcode in enumerate(gcode_list):
                if ';gimage' in gcode:
                    image_gcode = ';;gimage:' + self.create_snapshot((200, 200))
                    #self.scene.gcode_dict[build_plate_number][index] = self.scene.gcode_dict[build_plate_number][index].replace(';gimage', '')
                    self.scene.gcode_dict[0][0] = image_gcode + self.scene.gcode_dict[0][0]
                if ';simage' in gcode:
                    image_gcode = ';simage:' + self.create_snapshot((100, 100))
                    #self.scene.gcode_dict[build_plate_number][index] = self.scene.gcode_dict[build_plate_number][index].replace(';simage', '')
                    self.scene.gcode_dict[0][0] = image_gcode + self.scene.gcode_dict[0][0]
