# Copyright (c) 2020 DhanOS
# The LotmaxxSnapshot is released under the terms of the AGPLv3 or higher.

from UM.Extension import Extension
from UM.Application import Application
from UM.Logger import Logger

from cura.Snapshot import Snapshot


# Main class
class LotmaxxSnapshot(Extension):

    # Init
    def __init__(self):
        super().__init__()

        # Add a hook when a G-code is about to be written to a file
        Application.getInstance().getOutputDeviceManager().writeStarted.connect(self.add_snapshot_to_gcode)

        # Get a scene handler
        self.scene = Application.getInstance().getController().getScene()

    # Takes a snapshot image and encodes it
    def create_snapshot(self, size):

        # Take a snapshot of given size
        snapshot = Snapshot.snapshot(width=size[0], height=size[1])

        # Used for debugging
        #snapshot.save(os.path.dirname(__file__) + "/test.png")

        # Smapshot gcode
        gcode = ''

        # Iterate all of the image  pixels
        for y in range(snapshot.height()):
            for x in range(snapshot.width()):

                # Take pixel data
                pixel = snapshot.pixelColor(x, y)

                # Convert to 16-bit (2-byte) -encoded image
                rgb16 = (pixel.red() >> 3 << 11) | (pixel.green() >> 2 << 5) | (pixel.blue() >> 3)

                # Convert pixel data into hex values
                rgb16_hex = "{:04x}".format(rgb16)

                # Change rndianess to little-endian
                rgb16_hex_le = rgb16_hex[2:4] + rgb16_hex[0:2]

                # Add resulting values to a gcode
                gcode += rgb16_hex_le

            # Add a G-code code
            gcode += '\rM10086 ;'

        # Add new line break
        gcode += '\r'

        # Return resulting G-code
        return gcode

    # G-code hook
    def add_snapshot_to_gcode(self, output_device):

        # If there's no G-code - return
        if not hasattr(self.scene, "gcode_dict") or not self.scene.gcode_dict:
            Logger.log("w", "Scene does not contain any gcode")
            return

        # Enumerate G-code objects
        for build_plate_number, gcode_list in self.scene.gcode_dict.items():
            for index, gcode in enumerate(gcode_list):

                # If there is ;gimage anywhere, add encoded snapshot image at the beginning
                if ';gimage' in gcode:
                    # Create a G-code
                    image_gcode = ';;gimage:' + self.create_snapshot((200, 200))
                    # Remove the tag
                    #self.scene.gcode_dict[build_plate_number][index] = self.scene.gcode_dict[build_plate_number][index].replace(';gimage', '')
                    # Add image G-code to the beginning of the G-code
                    self.scene.gcode_dict[0][0] = image_gcode + self.scene.gcode_dict[0][0]

                # If there is ;simage anywhere, add encoded snapshot image at the beginning
                if ';simage' in gcode:
                    # Create a G-code
                    image_gcode = ';simage:' + self.create_snapshot((100, 100))
                    # Remove the tag
                    #self.scene.gcode_dict[build_plate_number][index] = self.scene.gcode_dict[build_plate_number][index].replace(';simage', '')
                    # Add image G-code to the beginning of the G-code
                    self.scene.gcode_dict[0][0] = image_gcode + self.scene.gcode_dict[0][0]
