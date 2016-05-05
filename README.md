# lz4_container

python container for lz4


lz4 is a fast compression， homepage http://cyan4973.github.io/lz4/

here I write xlz4.py to create container for lz4




structure of each block in *.lz4r:

	|-- header<list using hex and base64>
		|-- dir<str>
		|-- filename<str>
		|-- block count of filename<int>
		|-- size of content<int>
	|-- content using lz4.compress<lz4 str>




### Dependence

- linux (can't run on win)
- python2.7x
- python library: lz4, docopt

### Usage


before use:

	pip install -r dependence

cmd:

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

cmd eg:


	# eg for compress. 
	python xlz4.py -c test.lz4r test/

	# eg for decompress.
	python xlz4.py -x test.lz4r

	# eg for decompress.
	python xlz4.py -x test.lz4r test2


	# eg for list of *.lz4r.
	python xlz4.py -l test.lz4r

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

now you can change dir when decompress:

	xlz4.py -x <dir_name.lz4r> <dir_name>

now you can list filenames in *.lz4r:

	xlz4.py -l <dir_name.lz4r>

debug for Path Dependence
