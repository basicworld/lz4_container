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
# pep8
# Here I defind a container for lz4,
# use following cmd you can
# compress and decompress files in dir_name to dir_name.lz4r

# - lz4 -c dir_name.lz4r dir_name
# - lz4 -x dir_name.lz4r

# lz4r file is a pickle file, each pickle_item include:
# file_name, file_dir, content(using lz4)
import os
import pickle
import sys
# import lz4
from Queue import Queue


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
            raise ValueError("Invalid mode ('%s')" % ctype)

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

        # save
        file_name = self.kwargs.get('file_name')
        if file_name:
            full_file_name = os.path.abspath(file_name)
            full_file_dir = os.path.dirname(full_file_name)
            os.makedirs(full_file_dir) if not os.path.isdir(full_file_dir) \
                else None
            # open file for compress
            f = open(full_file_name, 'wb')

            # get all files in dir_name and compress them using lz4
            for parent, dirnames, filenames in os.walk(dir_name):
                for filename in filenames:
                    fullfilename = os.path.join(parent, filename)
                    print len(open(fullfilename, 'rb').read())
                    print len(lz4.compress(open(fullfilename, 'rb').read()))
                    pickle.dump({
                              'file_name': os.path.basename(filename),
                              'file_dir': parent,
                              # 'content': open(fullfilename, 'rb').read()
                              'content': lz4.compress(open(fullfilename,
                                                      'rb').read())
                              }, f)
            f.close()

        else:
            raise ValueError("file_name must be given")
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

        # decompress
        lz4_f = open(file_name, 'rb')
        while True:
            try:
                item = pickle.load(lz4_f)
                file_dir = (item.get('file_dir'))
                os.makedirs(file_dir) if not os.path.isdir(file_dir) else None
                with open(os.path.join(file_dir, item['file_name']),
                          'wb') as item_f:
                    # item_f.write(item['content'])
                    item_f.write(lz4.decompress(item['content']))
            except EOFError as e:  # when empty
                break
        lz4_f.close()


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
