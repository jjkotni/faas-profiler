/*The purpose of the module is to import pkey_mprotect system calls 
  to allocate memory with a protection key*/

#include "Python.h"
#include "marshal.h"
#include "pythread.h"
#include "structmember.h"
#include <float.h>
#include <signal.h>

#include <unistd.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <sys/mman.h>

typedef struct {
    PyMemAllocatorEx alloc;

    size_t malloc_size;
    size_t calloc_nelem;
    size_t calloc_elsize;
    void *realloc_ptr;
    size_t realloc_new_size;
    void *free_ptr;
    void *ctx;
} alloc_hook_t;

static void* pkey_malloc(void* ctx, size_t size)
{
    void *ptr;
	printf("Entered pkey malloc!\n");
    ptr = PyMem_RawMalloc(size);
    //allocate a pkey if it doesn't already exist
    int pkey = syscall(330, 0, 0);
    printf("Allocated pkey is %d!\n", pkey);
    syscall(329, (int *)ptr, size, PROT_READ|PROT_WRITE, pkey);

    return ptr;
}

static void* pkey_calloc(void* ctx, size_t nelem, size_t elsize)
{
	printf("Entered hook calloc!\n");
    alloc_hook_t *hook = (alloc_hook_t *)ctx;
    hook->ctx = ctx;
    hook->calloc_nelem = nelem;
    hook->calloc_elsize = elsize;
    return hook->alloc.calloc(hook->alloc.ctx, nelem, elsize);
}

static void* pkey_realloc(void* ctx, void* ptr, size_t new_size)
{
	printf("Entered hook realloc!\n");
    alloc_hook_t *hook = (alloc_hook_t *)ctx;
    hook->ctx = ctx;
    hook->realloc_ptr = ptr;
    hook->realloc_new_size = new_size;
    return hook->alloc.realloc(hook->alloc.ctx, ptr, new_size);
}

static void pkey_free(void *ctx, void *ptr)
{
	printf("Entered hook free!\n");
    alloc_hook_t *hook = (alloc_hook_t *)ctx;
    hook->ctx = ctx;
    hook->free_ptr = ptr;
    hook->alloc.free(hook->alloc.ctx, ptr);
}

static PyObject *
test_setallocators(PyMemAllocatorDomain domain)
{
    PyObject *res = NULL;
    const char *error_msg;
    alloc_hook_t hook;
    PyMemAllocatorEx alloc;
    size_t size, size2, nelem, elsize;
    void *ptr, *ptr2;

    memset(&hook, 0, sizeof(hook));

    alloc.ctx = &hook;
    alloc.malloc = &pkey_malloc;
    alloc.calloc = &pkey_calloc;
    alloc.realloc = &pkey_realloc;
    alloc.free = &pkey_free;
    PyMem_GetAllocator(domain, &hook.alloc);
    PyMem_SetAllocator(domain, &alloc);

    /* malloc, realloc, free */
    size = 42;
    hook.ctx = NULL;
    switch(domain)
    {
    case PYMEM_DOMAIN_RAW: ptr = PyMem_RawMalloc(size); break;
    case PYMEM_DOMAIN_MEM: ptr = PyMem_Malloc(size); break;
    case PYMEM_DOMAIN_OBJ: ptr = PyObject_Malloc(size); break;
    default: ptr = NULL; break;
    }

#define CHECK_CTX(FUNC) \
    if (hook.ctx != &hook) { \
        error_msg = FUNC " wrong context"; \
        goto fail; \
    } \
    hook.ctx = NULL;  /* reset for next check */

    if (ptr == NULL) {
        error_msg = "malloc failed";
        goto fail;
    }
    CHECK_CTX("malloc");
    if (hook.malloc_size != size) {
        error_msg = "malloc invalid size";
        goto fail;
    }

    size2 = 200;
    switch(domain)
    {
    case PYMEM_DOMAIN_RAW: ptr2 = PyMem_RawRealloc(ptr, size2); break;
    case PYMEM_DOMAIN_MEM: ptr2 = PyMem_Realloc(ptr, size2); break;
    case PYMEM_DOMAIN_OBJ: ptr2 = PyObject_Realloc(ptr, size2); break;
    default: ptr2 = NULL; break;
    }

    if (ptr2 == NULL) {
        error_msg = "realloc failed";
        goto fail;
    }
    CHECK_CTX("realloc");
    if (hook.realloc_ptr != ptr
        || hook.realloc_new_size != size2) {
        error_msg = "realloc invalid parameters";
        goto fail;
    }

    switch(domain)
    {
    case PYMEM_DOMAIN_RAW: PyMem_RawFree(ptr2); break;
    case PYMEM_DOMAIN_MEM: PyMem_Free(ptr2); break;
    case PYMEM_DOMAIN_OBJ: PyObject_Free(ptr2); break;
    }

    CHECK_CTX("free");
    if (hook.free_ptr != ptr2) {
        error_msg = "free invalid pointer";
        goto fail;
    }

    /* calloc, free */
    nelem = 2;
    elsize = 5;
    switch(domain)
    {
    case PYMEM_DOMAIN_RAW: ptr = PyMem_RawCalloc(nelem, elsize); break;
    case PYMEM_DOMAIN_MEM: ptr = PyMem_Calloc(nelem, elsize); break;
    case PYMEM_DOMAIN_OBJ: ptr = PyObject_Calloc(nelem, elsize); break;
    default: ptr = NULL; break;
    }

    if (ptr == NULL) {
        error_msg = "calloc failed";
        goto fail;
    }
    CHECK_CTX("calloc");
    if (hook.calloc_nelem != nelem || hook.calloc_elsize != elsize) {
        error_msg = "calloc invalid nelem or elsize";
        goto fail;
    }

    hook.free_ptr = NULL;
    switch(domain)
    {
    case PYMEM_DOMAIN_RAW: PyMem_RawFree(ptr); break;
    case PYMEM_DOMAIN_MEM: PyMem_Free(ptr); break;
    case PYMEM_DOMAIN_OBJ: PyObject_Free(ptr); break;
    }

    CHECK_CTX("calloc free");
    if (hook.free_ptr != ptr) {
        error_msg = "calloc free invalid pointer";
        goto fail;
    }

    Py_INCREF(Py_None);
    res = Py_None;
    goto finally;

fail:
    PyErr_SetString(PyExc_RuntimeError, error_msg);

finally:
    PyMem_SetAllocator(domain, &hook.alloc);
    return res;

#undef CHECK_CTX
}

static PyObject *
test_pymem_setrawallocators(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    return test_setallocators(PYMEM_DOMAIN_RAW);
}

static PyObject *
test_pymem_setallocators(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    return test_setallocators(PYMEM_DOMAIN_MEM);
}

static PyObject *
test_pyobject_setallocators(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    return test_setallocators(PYMEM_DOMAIN_OBJ);
}

//My code

/*
void* PyMem_RawMalloc(size_t n)
{
	printf("Entered raw allocator!\n");;
}

void* PyMem_Malloc(size_t n)
{
	printf("Entered my allocator in PyMem_Malloc!\n");;
}
*/

static PyObject *method_fputs(PyObject *self, PyObject *args) {
    char *str, *filename = NULL;
    int bytes_copied = -1;

    /* Parse arguments */
    if(!PyArg_ParseTuple(args, "ss", &str, &filename)) {
        return NULL;
    }

    FILE *fp = fopen(filename, "w");
    bytes_copied = fputs(str, fp);
    fclose(fp);

    return PyLong_FromLong(bytes_copied);
}

static PyMethodDef mpkMemAllocators[] = {
    {"fputs", method_fputs, METH_VARARGS, "Python interface for fputs C library function"},
    //{"PyMem_RawMalloc", PyMem_RawMalloc, 0, "Custom raw allocator"},
    //{"PyMem_Malloc", PyMem_Malloc, 0, "Custom allocator"},
	{"test_pymem_setrawallocators",test_pymem_setrawallocators,  METH_NOARGS},
    {"test_pymem_setallocators",test_pymem_setallocators,        METH_NOARGS},
    {"test_pyobject_setallocators",test_pyobject_setallocators,  METH_NOARGS},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef mpkmemallocmodule = {
    PyModuleDef_HEAD_INIT,
    "mpkmemalloc",
    "Python interface for custom MPK memory allocators",
    -1,
    mpkMemAllocators
};

PyMODINIT_FUNC PyInit_mpkmemalloc(void) {
    return PyModule_Create(&mpkmemallocmodule);
}