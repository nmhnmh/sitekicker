import os
import logging
import itertools
import math
import re
from multiprocessing import Pool

from wand.image import Image as wandImage

from .entry_file import EntryFile

def compress(images):
    pass


def resize(src, dest, target_width, compress=75):
    COMPRESS_OPTION=compress
    name = os.path.basename(src)
    matches = re.match(r'(.+)\.([^\.]+)', name)
    resize_name = matches.group(1) + '-' + str(target_width) + 'px.' + matches.group(2)
    dest_path = os.path.join(dest, resize_name)
    logging.info("Resize image from %s to %s", src, dest_path)
    with wandImage(filename=src) as im:
        width, height = im.size
        logging.debug("Original size, width: %ipx, height: %ipx, target width: %ipx" % (width, height, target_width))
        if width<target_width:
            with im.clone() as newim:
                newim.compression_quality = COMPRESS_OPTION
                save_name=matches.group(1) + '-' + str(width) + 'px.' + matches.group(2)
                logging.debug("Resize(save-no-resize) %s to %s", src, save_name)
                newim.save(filename=os.path.join(dest, save_name))
        else:
            ratio = height/width
            new_height = int(ratio * target_width)
            logging.debug("Resize %s to new size: %ix%i", src, target_width, new_height)
            with im.clone() as newim:
                newim.resize(target_width, new_height)
                newim.compression_quality = COMPRESS_OPTION
                newim.save(filename=dest_path)

class EntryImage(EntryFile):
    def __init__(self, entry, src):
        super().__init__(entry, src)

    def __str__(self):
        return "Entry image: %s" % self.src

    def snapshot(self):
        self.entry.site.snapshots[self.src] = os.path.getmtime(self.src)

    def is_changed(self):
        if self.src in self.entry.site.snapshots:
            return os.path.getmtime(self.src) > self.entry.site.snapshots[self.src]
        else:
            return True

    def process(self):
        if not self.is_changed():
            logging.debug("Snapshot shows no change occurred, skipped.")
            return
        combined_widths = self.entry.site.build_options['responsive_image_sizes']
        if not self.entry.site.cli_options.no_parallel:
            args = [(self.src, self.entry.output_path, w) for w in combined_widths]
            # placeholder image resize
            args.append((self.src, self.entry.output_path, self.entry.site.build_options['image_placeholder_size'], 15))
            with Pool(os.cpu_count()) as pool:
                pool.starmap(resize, args)
        else:
            for width in combined_widths:
                resize(self.src, self.entry.output_path, width)
            # placeholder image resize
            resize(self.src, self.entry.output_path, self.entry.site.build_options['image_palceholder_size'], 15)
        # Snapshot
        self.snapshot()
