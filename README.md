# lz4_container

python container for lz4


lz4 is a fast compression， homepage http://cyan4973.github.io/lz4/

here I write xlz4.py to create container for lz4


function:

- compress dir to *.lz4r
- compress file to *.lz4r
- show filenames in *.lz4r
- decompress *.lz4r


structure of each block in *.lz4r:

	|-- header<list using hex and base64>
		|-- dir<str or None>
		|-- filename<str or None>
		|-- block count of filename<int>
		|-- size of content<int>
	|-- compressed content <str using lz4.compress>





### Dependence

- linux (`lz4` can't run on win)
- python2.7x (not test on python3.x)
- python library: `lz4`, `docopt`

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
	# available on linux
	python xlz4.py -c test.lz4r test/

	# eg for decompress.
	# available on linux
	python xlz4.py -x test.lz4r

	# eg for decompress.
	# available on linux
	python xlz4.py -x test.lz4r test2


	# eg for list of *.lz4r.
	# available on linux and win
	python xlz4.py -l test.lz4r

### Note


- coding in line with `pep8`
- files in `test` are from nginx source code
- had not been tested on `mac` env, feel free to feed back any bug occurred on `mac`
- don't try to install lz4 on windows (#2115).
click here for more info: https://github.com/steeve/python-lz4/issues/27


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

multi types of file tested: dir, txt_like file, jpg, pdf, gif, mp3...

improve the robustness：

- test if it's *.lz4r file or not by block_header

simplify header of block: remove unnecessary info

