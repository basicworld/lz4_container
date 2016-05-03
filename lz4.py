# -*- coding:utf8 -*-
"""
Usage:
    lz4.py -c <dir_name.lz4r> <dir_name>
    lz4.py -x <dir_name.lz4r>

Arguments:
    dir_name.lz4r compressed file_name
    dir_name      dir_name

Options:
    -h --help     show this help
    -c            compress
    -x            decompress
"""
# - lz4 -c dir_name.lz4r dir_name
# - lz4 -x dir_name.lz4r
# pep8
import os


class Lz4Container(object):
    def __init__(self, ctype, **kwargs):
        """
        Lz4Container(ctype, **kwargs)
        @ctype: `c` for compress, `x` for decompress
        @kwargs['dir_name']     dir_name for compress
        @kwargs['file_name']    file_name for compress and decompress
        """
        # raise error if open in wrong mode
        if ctype not in ('c', 'x'):
            raise TypeError("ValueError: Invalid mode ('%s')" % ctype)

        self.ctype = ctype
        self.kwargs = kwargs

    def compress(self):
        """
        compress files in `dir_name` and save as `file_name`

        todo: howto deal with subdir?
        """
        # raise error for wrong mode
        if self.ctype != 'c':
            raise IOError('File not open for compress')

        # test if dir exsit
        dir_name = self.kwargs.get('dir_name')
        if not (dir_name and os.path.isdir(dir_name)):
            raise IOError("No such file or directory: '%s'" % dir_name)
        print('compressing')

    def decompress(self):
        """
        decompress `file_name`
        """
        # raise error for wrong mode
        if self.ctype != 'x':
            raise IOError('File not open for decompress')

        # test if file exsit
        file_name = self.kwargs.get('file_name')
        if not (file_name and os.path.isfile(file_name)):
            raise IOError("No such file or directory: '%s'" % file_name)
        print('decompressing')

        file_name = os.path.abspath(file_name)

        # mkdir for decompress
        file_dir = os.path.dirname(file_name)
        os.makedirs(file_dir) if not os.path.isdir(file_dir) else None

        # decompress


def api(dir_name, file_name, ctype):
    """
    api(dir_name, file_name, ctype)

    function: api for lz4 container
    @dir_name     dir_name for compress
    @file_name    file_name for compress and decompress
    @ctype: `c` for compress, `x` for decompress
    """
    # print (dir_name, file_name, ctype)
    if ctype == 'c':
        lz4app = Lz4Container(ctype, dir_name=dir_name, file_name=file_name)
        lz4app.compress()
    elif ctype == 'x':
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
    print(args)
    ctype = 'c' if args.get('-c') else 'x'  # compress or decompress
    api(args.get('<dir_name>'), args.get('<dir_name.lz4r>'), ctype)


if __name__ == '__main__':
    cmd()
