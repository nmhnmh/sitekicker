import os
import logging
import itertools
import math
import re
from multiprocessing import Pool
import subprocess
import shlex
from ..util import get_image_size
from .entry_file import EntryFile

def resize(src, dest, target_width, quality=82):
    logging.debug("IM Resize Image from {} to {}, target_width: {}px, qulity: {}%".format(src, dest, target_width, quality))
    resize_command = "mogrify -write {OUTPUT_PATH} -filter Triangle -define filter:support=2 -thumbnail {OUTPUT_WIDTH} -unsharp 0.25x0.08+8.3+0.045 -dither None -posterize 136 -quality {QUALITY} -define jpeg:fancy-upsampling=off -define png:compression-filter=5 -define png:compression-level=9 -define png:compression-strategy=1 -define png:exclude-chunk=all -interlace none -colorspace sRGB {INPUT_PATH}"
    name = os.path.basename(src)
    matches = re.match(r'(.+)\.([^\.]+)', name)
    width, height = get_image_size(src)
    logging.debug("Original size, width: %ipx, height: %ipx, target width: %ipx" % (width, height, target_width))
    if width<target_width:
        save_name=matches.group(1) + '-' + str(width) + 'px.' + matches.group(2)
        dest_path = os.path.join(dest, save_name)
        logging.debug("Resize(save-no-resize) %s to %s", src, dest_path)
        subprocess.call(resize_command.format(OUTPUT_PATH=shlex.quote(dest_path), OUTPUT_WIDTH=width, QUALITY=quality, INPUT_PATH=shlex.quote(src)), shell=True)
    else:
        ratio = height/width
        new_height = int(ratio * target_width)
        resize_name = matches.group(1) + '-' + str(target_width) + 'px.' + matches.group(2)
        dest_path = os.path.join(dest, resize_name)
        logging.debug("Resize %s to new size: %ix%i, saved to %s", src, target_width, new_height, dest_path)
        subprocess.call(resize_command.format(OUTPUT_PATH=shlex.quote(dest_path), OUTPUT_WIDTH=target_width, QUALITY=quality, INPUT_PATH=shlex.quote(src)), shell=True)

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
