import os
from PIL import Image
import logging

from .entry_file import EntryFile

class EntryImage(EntryFile):
    def __init__(self, entry, src):
        super().__init__(entry, src)

    def __str__(self):
        return "Entry image: %s" % self.src

    def resize(self):
        dest = os.path.join(
            self.entry.output_dir,
            os.path.basename(self.src)
        )
        logging.debug("Resize image from %s to %s", self.src, dest)
        im = Image.open(self.src)
        width, height = im.size
        MAX_WIDTH = self.entry.site.options['image_options']['resize']['max-width']
        if width < MAX_WIDTH:
            im.save(dest)
        else:
            ratio = height/width
            new_height = int(ratio * MAX_WIDTH)
            logging.debug("Resize %s to new size: %ix%i", self, MAX_WIDTH, new_height)
            newim = im.resize((MAX_WIDTH, new_height))
            newim.save(dest)

    def compress(self):
        pass

    def watermark_text(self):
        # newim = watermark.watermark(newim, Image.open(os.path.join(self.options.working_dir, 'assets/images/watermark.png')), (MAX_WIDTH-400, new_height-60))
        pass

    def watermark_image(self):
        pass

    def generate_thumb(self):
        pass
