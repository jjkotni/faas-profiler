from distutils.core import setup, Extension

def main():
    setup(name="mpkmemalloc",
          version="1.0.0",
          description="Python interface for MPK memory allocators",
          author="Swaroop Kotni",
          author_email="jjkotni@github.com",
          ext_modules=[Extension("mpkmemalloc", ["mpkmemallocmodule.c"])])

if __name__ == "__main__":
    main()