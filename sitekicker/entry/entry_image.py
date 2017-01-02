import os
import logging
import itertools
import math
import re
from multiprocessing import Pool

from wand.image import Image as wandImage

from .entry_file import EntryFile


def resize(src, dest, target_width):
    name = os.path.basename(src)
    matches = re.match(r'(.+)\.([^\.]+)', name)
    resize_name = matches.group(1) + '-' + str(target_width) + 'px.' + matches.group(2)
    dest_path = os.path.join(dest, resize_name)
    logging.info("Resize image from %s to %s", src, dest_path)
    with wandImage(filename=src) as im:
        width, height = im.size
        logging.debug("Original size, width: %ipx, height: %ipx" % (width, height))
        if width < target_width:
            im.save(filename=dest_path)
        else:
            ratio = height/width
            new_height = int(ratio * target_width)
            logging.debug("Resize %s to new size: %ix%i", src, target_width, new_height)
            with im.clone() as newim:
                newim.resize(target_width, new_height)
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
        sizes = [384, 768]
        dpis = [1, 1.5, 2, 3]
        combined_widths = set(math.floor(w*r) for w, r in itertools.product(sizes, dpis))
        if not self.entry.site.cli_options.no_parallel:
            args = [(self.src, self.entry.output_path, w) for w in combined_widths]
            args.append((self.src, self.entry.output_path, 96))
            with Pool(os.cpu_count()) as pool:
                pool.starmap(resize, args)
        else:
            for width in combined_widths:
                resize(self.src, self.entry.output_path, width)
            # LQIP resize
            resize(self.src, self.entry.output_path, 96)
        # Snapshot
        self.snapshot()
