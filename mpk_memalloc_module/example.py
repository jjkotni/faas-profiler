import mpkmemalloc as mpk
import sys

def main(argv):
    sample_arr = [1,2,3]
    print(sample_arr[1])
    mpk.PyMem_RawMalloc(2)
    

if __name__ == "__main__":
    main(sys.argv)
