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
# Here I defind a container for lz4,
# use following cmd you can
# compress and decompress files in dir_name to dir_name.lz4r

# - lz4 -c dir_name.lz4r dir_name
# - lz4 -x dir_name.lz4r

# lz4r file is a json file, each json_item include:
# file_name, file_dir, content(using lz4)

# lz4 will not work if run on win platform
import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import base64
WINPLAT = ('win' in sys.platform)
if not WINPLAT:
    import lz4

a2b_hex = base64.binascii.a2b_hex
hexlify = base64.binascii.hexlify


class Lz4Container(object):
    def __init__(self, ctype, **kwargs):
        """
        Lz4Container(ctype, **kwargs)
        @ctype: `c` for compress, `x` for decompress, `l` for list of files
        @kwargs['dir_name']     dir_name for compress
        @kwargs['file_name']    file_name for compress and decompress
        """
        # raise error if open in wrong mode
        if ctype not in ('c', 'x', 'l'):
            raise ValueError("Invalid mode ('%s')" % ctype)

        self.ctype = ctype
        self.kwargs = kwargs
        self.ok = False

    def compress(self, blk_size=64):
        """
        compress files in `dir_name` and save as `file_name`
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
        file_name = self.kwargs.get('file_name', os.path.basename(dir_name))
        if not file_name.endswith('.lz4r'):
            file_name = file_name + '.lz4r'

        full_file_name = os.path.abspath(file_name)
        full_file_dir = os.path.dirname(full_file_name)
        os.makedirs(full_file_dir) if not os.path.isdir(full_file_dir) \
            else None

        # open file to save
        outfile = open(full_file_name, 'wb')
        if self.type_of_dir_name == 'dir':
            # get all files in dir_name and compress them using lz4
            for parent, dirnames, infile_names in os.walk(dir_name):
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

                        # header for blk info
                        header = [parent,  # dir
                                  os.path.basename(infile_name),
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
                header = ['./',  # dir
                          os.path.basename(dir_name),
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
        while True:
            header = infile.readline()  # file header
            if not header:
                break
            # decode header
            header = json.loads(base64.decodestring(a2b_hex(header.strip())))

            # print list of filename if l
            if self.ctype == 'l':
                if (header[2] == 0):
                    print(header[1])
                infile.seek(header[-1], 1)
                continue

            content = infile.read(header[-1])  # header[-1]: size of content
            file_dir = header[0]  # header[0]: dir of origin file

            # change decompress dir to replcae_dir_name
            if replcae_dir_name and file_dir:
                drive, sub_dir = os.path.splitdrive(file_dir)
                if sub_dir:
                    try:  # in case of any error
                        split_sub_dir = sub_dir.split('/')
                        if split_sub_dir[0]:  # not startswith /
                            split_sub_dir[0] = replcae_dir_name
                        elif split_sub_dir[1]:  # startswith /
                            split_sub_dir[1] = replcae_dir_name
                        sub_dir = '/'.join(split_sub_dir)
                        file_dir = os.path.join(drive, sub_dir)
                    except:
                        raise
            # create dir
            os.makedirs(file_dir) if not os.path.isdir(file_dir) else None
            # save file
            open_mode = 'wb' if (header[2] == 0) else 'ab'  # newfile or not
            with open(os.path.join(file_dir, header[1]), open_mode) as outfile:
                if WINPLAT:
                    outfile.write(content)
                else:
                    outfile.write(lz4.decompress(content))
                outfile.flush()
                del content

        infile.close()
        self.ok = True


def api(dir_name, file_name, ctype):
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
