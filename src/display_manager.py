import os
from inky.auto import auto
from utils.image_utils import resize_image, change_orientation
from plugins.plugin_registry import get_plugin_instance
from IT8951.display import AutoEPDDisplay
from PIL import Image, ImageDraw, ImageFont
from IT8951 import constants

class DisplayManager:
    def __init__(self, device_config):
        """Manages the display and rendering of images."""
        self.device_config = device_config

        print('Initializing EPD...')
        
        self.inky_display = AutoEPDDisplay(vcom=-1.41, rotate=None, mirror=None, spi_hz=24000000)

        # store display resolution in device config
        if not device_config.get_config("resolution"):
            device_config.update_value("resolution",[int(self.inky_display.width), int(self.inky_display.height)], write=True)

    def display_image(self, image, image_settings=[]):
        """Displays the image provided, applying the image_settings."""
        if not image:
            raise ValueError(f"No image provided.")

        # Save the image
        image.save(self.device_config.current_image_file)

        # Resize and adjust orientation
        image = change_orientation(image, self.device_config.get_config("orientation"))
        image = resize_image(image, self.device_config.get_resolution(), image_settings)

        # Display the image on the Inky display
        self.display_image_8bpp(self.inky_display, image)

    @staticmethod
    def display_image_8bpp(display, img):
        # clearing image to white
        display.frame_buf.paste(0xFF, box=(0, 0, display.width, display.height))


        # TODO: this should be built-in
        dims = (display.width, display.height)

        img.thumbnail(dims)
        paste_coords = [dims[i] - img.size[i] for i in (0,1)]  # align image with bottom of display
        display.frame_buf.paste(img, paste_coords)
        display.draw_full(constants.DisplayModes.GC16)