/*The purpose of the module is to import pkey_mprotect system calls 
  to allocate memory with a protection key*/

#include <Python.h>

void* PyMem_RawMalloc(size_t n)
{
	printf("Entered raw allocator!\n");
}

void* PyMem_Malloc(size_t n)
{
	printf("Entered my allocator in PyMem_Malloc!\n");
}

static PyMethodDef mpkMemAllocators[] = {
    {"PyMem_RawMalloc", PyMem_RawMalloc, METH_VARARGS, "Custom raw allocator"},
    {"PyMem_Malloc", PyMem_Malloc, METH_VARARGS, "Custom allocator"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef mpkmodule = {
    PyModuleDef_HEAD_INIT,
    "fputs",
    "Python interface for the fputs C library function",
    -1,
    FputsMethods
};