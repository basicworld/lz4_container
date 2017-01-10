# -*- coding:utf8 -*-
"""
Usage:
    xlz4.py -c <dir_name.lz4r> <dir_name>
    xlz4.py -x <dir_name.lz4r> [<dir_name>]
    xlz4.py -l <dir_name.lz4r>

Arguments:
    dir_name.lz4r file_name
    dir_name      dir_name

Options:
    -h --help     show this help
    -c            compress
    -x            decompress
    -l            list the filename in lz4r
"""
# pep8

# - lz4 -c dir_name.lz4r dir_name
# - lz4 -x dir_name.lz4r

import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import base64
WINPLAT = ('win' in sys.platform)
SEP = '/'
if not WINPLAT:
    import lz4

a2b_hex = base64.binascii.a2b_hex
hexlify = base64.binascii.hexlify
unify_dir = lambda x: x.replace('\\', '/')


class Lz4Container(object):
    def __init__(self, ctype, **kwargs):
        """
        Lz4Container(ctype, **kwargs)
        @ctype: type of Lz4Container obj,
                `c` for compress,
                `x` for decompress,
                `l` for list of files
        @kwargs['dir_name']     dir_name for compress and decompress
        @kwargs['file_name']    file_name for compress and decompress

        whis Container will work just like linux's `tar` cmd when use on win,
        because `lz4` can't install on win, which means, *.lz4r create on win
        can't decompress on linux, vice versa.
        """
        # raise error if open in wrong mode
        if ctype not in ('c', 'x', 'l'):
            raise ValueError("Invalid mode ('%s')" % ctype)

        self.ctype = ctype
        self.kwargs = kwargs
        self.ok = False  # use for api

    def compress(self, blk_size=64):
        """
        compress files in `dir_name` and save as `file_name`

        process of compressing each file:
        1, read and compress a block of file
        2, create header: [file_dir, file_name, block_count, block_size],
           encode header using hex for decompressing convenience
        3, write a block into *.lz4r: header, compressed_block
        4, jump to `1` if not at the end of file

        """
        # raise error for wrong mode
        if self.ctype != 'c':
            raise IOError('File not open for compress')

        # test if dir exsit
        dir_name = self.kwargs.get('dir_name')
        self.type_of_dir_name = None
        if (dir_name and os.path.isdir(dir_name)):
            self.type_of_dir_name = 'dir'
        elif (dir_name and os.path.isfile(dir_name)):
            self.type_of_dir_name = 'file'
        if not self.type_of_dir_name:
            raise IOError("No such file or directory: '%s'" % dir_name)

        # file_name is the outfile, namely *.lz4r
        dir_name = unify_dir(dir_name)
        base_dir_name = os.path.basename(dir_name.rstrip(SEP))
        file_name = self.kwargs.get('file_name', base_dir_name)
        if not file_name.endswith('.lz4r'):
            file_name = file_name + '.lz4r'

        full_file_name = os.path.abspath(file_name)
        full_file_dir = os.path.dirname(full_file_name)
        os.makedirs(full_file_dir) if not os.path.isdir(full_file_dir) \
            else None

        # remove old file if exist
        if os.path.isfile(full_file_name):
            os.remove(full_file_name)
        # get dir_name index in case of long dir_name
        base_dir_name_index = len(dir_name.rstrip(SEP).split(SEP)) - 1
        # open file to save
        outfile = open(full_file_name, 'wb')
        if self.type_of_dir_name == 'dir':
            # get all files in dir_name and compress them using lz4
            for parent, dirnames, infile_names in os.walk(dir_name):
                #
                parent = unify_dir(parent)
                header_dir = SEP.join(parent.split(SEP)[base_dir_name_index:])
                for infile_name in infile_names:
                    if WINPLAT:
                        infile_name = infile_name.decode('gbk')
                        parent = parent.decode('gbk')
                    full_infile_name = os.path.join(parent, infile_name)
                    # split file
                    infile = open(full_infile_name, 'rb')
                    blk_count = 0  # block count
                    while True:
                        blk = infile.read(blk_size * (2 ** 10))
                        if not blk:  # end if down
                            break
                        if not WINPLAT:
                            blk = lz4.compress(blk)

                        # header for blk:
                        # [dir, filename, blk_count, content size]
                        header = [(header_dir if blk_count == 0 else None),
                                  (infile_name if blk_count == 0 else None),
                                  blk_count,  # is new file or not
                                  len(blk)]  # bytes
                        blk_count += 1
                        b64str = base64.encodestring(json.dumps(header))
                        outfile.write(hexlify(b64str))
                        outfile.write('\n')
                        outfile.write(blk)
                        del blk
                    infile.close()

        # in case where dir_name is a file
        elif self.type_of_dir_name == 'file':
            # split file
            infile = open(dir_name, 'rb')
            blk_count = 0  # block count
            while True:
                blk = infile.read(blk_size * (2 ** 10))
                if not blk:  # end if down
                    break
                if not WINPLAT:
                    blk = lz4.compress(blk)

                # header for blk info
                header = [('./' if blk_count == 0 else None),
                          (os.path.basename(dir_name) if blk_count == 0 else
                           None),
                          blk_count,  # is new file or not
                          len(blk)]  # bytes
                blk_count += 1
                b64str = base64.encodestring(json.dumps(header))
                outfile.write(hexlify(b64str))
                outfile.write('\n')
                outfile.write(blk)
                del blk
            infile.close()
        outfile.flush()
        outfile.close()
        self.ok = True

    def decompress(self):
        """
        decompress `file_name`
        a *.lz4r file will be decompressed into default dir(default dir saved
        in header of *.lz4r's block), you can change default dir to where you
        want by giving `dir_name` in cmd

        process of decompressing each block in *.lz4r:
        1, get header
        2, get dir, filename, block_count, block_size
        3, create dir and file_obj if needed,
           auto overwrite files and dirs if exsit
        4, get file_content use block_size
        5, decompress file_content and write to file_obj
        """
        # raise error for wrong mode
        if self.ctype not in ('x', 'l'):
            raise IOError('File not open for decompress')

        # test if file exsit
        file_name = self.kwargs.get('file_name')
        if not (file_name and os.path.isfile(file_name)):
            raise IOError("No such file or directory: '%s'" % file_name)

        replcae_dir_name = self.kwargs.get('dir_name')

        # decompress
        infile = open(file_name, 'rb')
        outfile_name = None
        while True:
            header = infile.readline()  # file header
            if not header:
                break
            # decode header
            try:
                raw_json = base64.decodestring(a2b_hex(header.strip()))
                header = json.loads(raw_json)
            except TypeError as e:
                raise TypeError("'%s' is not lz4r_type file" % file_name)

            blk_count = header[2]  # header[2] saves the block_count of file

            # print list of filename if l
            if self.ctype == 'l':
                if (blk_count == 0):
                    print(header[1])  # header[1] saves filename
                infile.seek(header[-1], 1)
                continue

            file_dir = header[0]  # header[0]: dir of origin file
            if (blk_count == 0):  # means new file
                # change decompress dir to replcae_dir_name
                if replcae_dir_name and file_dir:
                    drive, sub_dir = os.path.splitdrive(file_dir)
                    if sub_dir:
                        split_sub_dir = unify_dir(sub_dir).split(SEP)
                        if split_sub_dir and len(split_sub_dir) > 0:
                            split_sub_dir[0] = unify_dir(replcae_dir_name)
                        elif split_sub_dir and len(split_sub_dir) > 1:
                            split_sub_dir[1] = unify_dir(replcae_dir_name)
                        file_dir = os.path.join(drive, SEP.join(split_sub_dir))
                # create dir
                try:
                    if not os.path.isdir(file_dir):
                        os.makedirs(file_dir)
                except WindowsError as e:
                    raise WindowsError("Fail to makedirs: %s" % file_dir)
                outfile_name = os.path.join(file_dir, header[1])
                open_mode = 'wb'
            else:  # other block of file
                open_mode = 'ab'
                # outfile_name should not be None
                if not outfile_name:
                    raise AssertionError('block missing')
            # save file
            with open(outfile_name, open_mode) as outfile:
                # header[-1]: size of content
                content = infile.read(header[-1])
                if WINPLAT:
                    outfile.write(content)
                else:
                    outfile.write(lz4.decompress(content))
                outfile.flush()
                del content

        infile.close()
        self.ok = True


def test(dir_name, file_name, ctype):
    """
    api(dir_name, file_name, ctype)

    function: api for lz4 container
    @dir_name     dir_name for compress
    @file_name    file_name for compress and decompress
    @ctype: `c` for compress, `x` for decompress, `l` for list of files
    """
    if ctype == 'c':
        lz4app = Lz4Container(ctype, dir_name=dir_name, file_name=file_name)
        lz4app.compress()
    elif ctype in ('x', 'l'):
        lz4app = Lz4Container(ctype, dir_name=dir_name, file_name=file_name)
        lz4app.decompress()
    else:
        raise TypeError("ValueError: Invalid mode ('%s')" % ctype)


def cmd():
    """
    function: command line
    """
    from docopt import docopt
    args = docopt(__doc__)
    if args.get('-c'):
        ctype = 'c'
    elif args.get('-x'):
        ctype = 'x'
    elif args.get('-l'):
        ctype = 'l'  # compress or decompress
    api(args.get('<dir_name>'), args.get('<dir_name.lz4r>'), ctype)


if __name__ == '__main__':
    cmd()
