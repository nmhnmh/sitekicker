import os
import logging
import re
import subprocess
import shlex
import shutil
from ..util import get_image_size
from .entry_file import EntryFile

def compress_resize_image(src, dest, target_width, quality=80, caches=None, full_build=False):
    options_cache_key = "{}-options".format(src)
    options_cache_value = "{},{}".format(target_width, quality)
    cache_hit = (
        src in caches and
        os.path.getmtime(src) == caches[src] and
        dest in caches and
        os.path.isfile(dest) and
        os.path.getmtime(dest) == caches[dest] and
        options_cache_key in caches and
        options_cache_value == caches[options_cache_key]
    )
    if caches is not None and not full_build and cache_hit:
        logging.debug("Cache hit for {}!".format(src))
        return
    logging.debug("IM Resize and Compress image from {} to {}, target_width: {}px, qulity: {}%".format(src, dest, target_width, quality))
    COMPRESS_CMD = "mogrify -write {OUTPUT_PATH} -thumbnail '{OUTPUT_WIDTH}x10000>' -filter Triangle -define filter:support=2 -unsharp 0.25x0.08+8.3+0.045 -dither None -posterize 136 -quality {QUALITY} -define jpeg:fancy-upsampling=off -define png:compression-filter=5 -define png:compression-level=9 -define png:compression-strategy=1 -define png:exclude-chunk=all -interlace none -colorspace sRGB {INPUT_PATH}"
    logging.debug("Copy and compress entry image from %s to %s" % (src, dest))
    subprocess.call(COMPRESS_CMD.format(
        OUTPUT_PATH=shlex.quote(dest),
        QUALITY=quality,
        OUTPUT_WIDTH=target_width,
        INPUT_PATH=shlex.quote(src)),
        shell=True
    )
    if caches is not None:
        caches[src] = os.path.getmtime(src)
        caches[dest] = os.path.getmtime(dest)
        caches[options_cache_key] = options_cache_value

class EntryImage(EntryFile):
    def __init__(self, entry, title, name):
        super().__init__(entry, title, name)
        self.real_width, self.real_height = get_image_size(self.fullpath) if not self.is_external else 0, 0
        matches = re.match(r'(.+)\.([^\.]+)', self.name)
        self.name_no_ext = matches.group(1) if matches else ''
        self.ext = matches.group(2) if matches else ''

    def check_file(self):
        if not self.is_external and not os.path.isfile(self.fullpath):
            self.file_exists=False
            raise Exception("Post [{} > {}] referencing a non-exist local image [{}]!".format(self.entry.id, self.title, self.name))

    def __str__(self):
        return "Entry image: %s" % self.fullpath

    def copy(self):
        logging.debug("Copy entry image from %s to %s" % (self.fullpath, self.dest_fullpath))
        dest_dir = os.path.dirname(self.dest_fullpath)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        if self.entry.site.build_options['compress_image']:
            task_arguments = (
                self.fullpath,
                self.dest_fullpath,
                self.entry.site.build_options['maximum_image_width'],
                self.entry.site.build_options['compress_image_quality'],
                self.entry.site.snapshots,
                self.entry.site.cli_options.full_build
            )
            if not self.entry.site.cli_options.no_parallel:
                self.entry.site.task_pool.apply_async(compress_resize_image, task_arguments)
            else:
                compress_resize_image(*task_arguments)
        else:
            shutil.copy(self.fullpath, self.dest_fullpath)

    def responsive_process(self):
        # generate process task array
        target_widths = self.entry.site.build_options['responsive_image_sizes']
        task_array=[]
        for tw in target_widths:
            if self.real_width<tw:
                save_name=self.name_no_ext + '-' + str(self.real_width) + 'px.' + self.ext
                new_dest_fullpath = os.path.join(os.path.dirname(self.dest_fullpath), save_name)
                logging.debug("Resize(save-no-resize) %s to %s", self.fullpath, new_dest_fullpath)
                arg=(
                    self.fullpath,
                    new_dest_fullpath,
                    self.real_width,
                    self.entry.site.build_options['compress_image_quality'],
                    self.entry.site.snapshots,
                    self.entry.site.cli_options.full_build
                )
            else:
                ratio = self.real_height/self.real_width
                new_height = int(ratio * tw)
                save_name = self.name_no_ext + '-' + str(tw) + 'px.' + self.ext
                new_dest_fullpath = os.path.join(os.path.dirname(self.dest_fullpath), save_name)
                logging.debug("Resize %s to new size: %ix%i, saved to %s", self.fullpath, tw, new_height, new_dest_fullpath)
                arg=(
                    self.fullpath,
                    new_dest_fullpath,
                    tw,
                    self.entry.site.build_options['compress_image_quality'],
                    self.entry.site.snapshots,
                    self.entry.site.cli_options.full_build
                )
            task_array.append(arg)
        # add placeholder image generation task
        task_array.append((
            self.fullpath,
            self.entry.dest_fullpath,
            self.entry.site.build_options['image_placeholder_size'],
            self.entry.site.build_options['image_placeholder_quality'],
            self.entry.site.snapshots,
            self.entry.site.cli_options.full_build
        ))
        # parallel or serial
        if not self.entry.site.cli_options.no_parallel:
            self.entry.site.task_pool.starmap_async(compress_resize_image, task_array)
        else:
            for task in task_array:
                compress_resize_image(*task)
