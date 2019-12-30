import sys
import os
import pdb
from optparse import OptionParser
from mpkmemalloc import test_pymem_setrawallocators, test_pymem_setallocators, test_pyobject_setallocator

sdef main(argv):
    test_pymem_setrawallocators()
    test_pymem_setallocators()
    test_pyobject_setallocators()
    a = [1,2]
    a.append(3)
	
if __name__ == "__main__":
    main(sys.argv)