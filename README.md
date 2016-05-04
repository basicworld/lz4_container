# lz4_container

python container for lz4 (lz4 homepage: https://github.com/mwotton/lz4hs)

### lz4

lz4 is a fast fast compression

here I write xlz4.py to create container for lz4

### Dependence

- linux (can't run on win)
- python2.7x
- python library: lz4, docopt

### Usage
	
	Usage:
	    xlz4.py -c <dir_name.lz4r> <dir_name>
	    xlz4.py -x <dir_name.lz4r>
	
	Arguments:
	    dir_name.lz4r compressed file_name
	    dir_name      dir_name
	
	Options:
	    -h --help     show this help
	    -c            compress
	    -x            decompress



### Note

- coding in line with `pep8`
- had not been tested on `mac` env, feel free to feed back any bug occurred on `mac`
- don't try to install lz4 on windows (#2115).
see here for more info: https://github.com/steeve/python-lz4/issues/27


### Development history

homepage of `lz4`

	https://github.com/Cyan4973/lz4

versions of `lz4` in multiple languages:

	http://cyan4973.github.io/lz4/

python `lz4` library:

	https://pypi.python.org/pypi/lz4/

use hex to save header

split file in case of memoryerror


