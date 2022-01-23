#ifndef Py_CPYTHON_PYSTATE_H
#  error "this header file must not be included directly"
#endif

#include "lock.h"

#ifdef __cplusplus
extern "C" {
#endif

#include "cpython/initconfig.h"

PyAPI_FUNC(int) _PyInterpreterState_RequiresIDRef(PyInterpreterState *);
PyAPI_FUNC(void) _PyInterpreterState_RequireIDRef(PyInterpreterState *, int);

PyAPI_FUNC(PyObject *) _PyInterpreterState_GetMainModule(PyInterpreterState *);

/* State unique per thread */

/* Py_tracefunc return -1 when raising an exception, or 0 for success. */
typedef int (*Py_tracefunc)(PyObject *, PyFrameObject *, int, PyObject *);

/* The following values are used for 'what' for tracefunc functions
 *
 * To add a new kind of trace event, also update "trace_init" in
 * Python/sysmodule.c to define the Python level event name
 */
#define PyTrace_CALL 0
#define PyTrace_EXCEPTION 1
#define PyTrace_LINE 2
#define PyTrace_RETURN 3
#define PyTrace_C_CALL 4
#define PyTrace_C_EXCEPTION 5
#define PyTrace_C_RETURN 6
#define PyTrace_OPCODE 7


typedef struct _err_stackitem {
    /* This struct represents an entry on the exception stack, which is a
     * per-coroutine state. (Coroutine in the computer science sense,
     * including the thread and generators).
     * This ensures that the exception state is not impacted by "yields"
     * from an except handler.
     */
    PyObject *exc_type, *exc_value, *exc_traceback;

    struct _err_stackitem *previous_item;

} _PyErr_StackItem;

struct mi_heap_s;
typedef struct mi_heap_s mi_heap_t;

// must match MI_NUM_HEAPS in mimalloc.h
#define Py_NUM_HEAPS 5

// _PyEventRc is defined in lock.h
typedef struct _PyEventRc _PyEventRc;
typedef union _Register Register;

struct mi_heap_s;
typedef struct mi_heap_s mi_heap_t;

// See pycore_pystate.h
struct PyThreadStateOS;
typedef struct PyThreadStateOS PyThreadStateOS;

struct Waiter;
typedef struct _PyEventRC _PyEventRC;

struct ThreadState;

// Forward declared from pycore_qsbr.h
struct qsbr;

// must match MI_NUM_HEAPS in mimalloc.h
#define Py_NUM_HEAPS 5

// The PyThreadState typedef is in Include/pystate.h.
struct _ts {
    Register *regs;
#ifdef HAVE_COMPUTED_GOTOS
    const void *opcode_targets[127];
#endif
    const uint8_t *pc;
    Register *stack;
    Register *maxstack;
    struct ThreadState *active;
    uintptr_t eval_breaker;
    PyObject **cargs;

    /* See Python/ceval.c for comments explaining most fields */

    struct _ts *prev;
    struct _ts *next;
    PyInterpreterState *interp;

    /* thread status (attached, detached, gc) */
    int32_t status;

    /* Borrowed reference to the current frame (it can be NULL) */
    PyFrameObject *frame;

    mi_heap_t *heaps[Py_NUM_HEAPS];

    int recursion_depth;
    char overflowed; /* The stack has overflowed. Allow 50 more calls
                        to handle the runtime error. */
    char recursion_critical; /* The current calls must not cause
                                a stack overflow. */
    int stackcheck_counter;

    /* 'tracing' keeps track of the execution depth when tracing/profiling.
       This is to prevent the actual trace/profile code from being recorded in
       the trace/profile. */
    int tracing;
    int use_tracing;

    /* The thread will not stop for GC or other stop-the-world requests.
     * Used for *short* critical sections that to prevent deadlocks between
     * finalizers and stopped threads. */
    int32_t cant_stop_wont_stop;

    Py_tracefunc c_profilefunc;
    Py_tracefunc c_tracefunc;
    PyObject *c_profileobj;
    PyObject *c_traceobj;

    /* The exception currently being raised */
    PyObject *curexc_type;
    PyObject *curexc_value;
    PyObject *curexc_traceback;

    /* The exception currently being handled, if no coroutines/generators
     * are present. Always last element on the stack referred to be exc_info.
     */
    _PyErr_StackItem exc_state;

    /* Pointer to the top of the stack of the exceptions currently
     * being handled */
    _PyErr_StackItem *exc_info;

    PyObject *dict;  /* Stores per-thread state */

    int gilstate_counter;

    PyObject *async_exc; /* Asynchronous exception to raise */
    unsigned long thread_id; /* Thread id where this tstate was created */

    uintptr_t fast_thread_id; /* Thread id used for object ownership */

    int trash_delete_nesting;
    PyObject *trash_delete_later;

    uintptr_t critical_section;

    _PyEventRc *done_event; /* Set when thread is about to exit */
    int daemon;

    uint64_t pydict_next_version; /* Dict version counter */

    int coroutine_origin_tracking_depth;

    PyObject *async_gen_firstiter;
    PyObject *async_gen_finalizer;

    PyObject *context;
    uint64_t context_ver;

    Py_ssize_t ref_total;

    /* Unique thread state id. */
    uint64_t id;

#ifdef HAVE_COMPUTED_GOTOS
    void *trace_target;
    void *trace_cfunc_target;
    void **opcode_targets_base;
#endif

    /* Local refcount for heap type objects */
    Py_ssize_t *local_refcnts;
    Py_ssize_t local_refcnts_size;

    struct method_cache_entry method_cache[(1 << MCACHE_SIZE_EXP)];

    /* XXX signal handlers should also be here */

};

// Alias for backward compatibility with Python 3.8
#define _PyInterpreterState_Get PyInterpreterState_Get

PyAPI_FUNC(PyThreadState *) _PyThreadState_Prealloc(PyInterpreterState *, _PyEventRc *done_event);

/* Similar to PyThreadState_Get(), but don't issue a fatal error
 * if it is NULL. */
PyAPI_FUNC(PyThreadState *) _PyThreadState_UncheckedGet(void);

PyAPI_FUNC(PyObject *) _PyThreadState_GetDict(PyThreadState *tstate);

PyAPI_FUNC(Py_ssize_t) _PyThreadState_GetRecursionDepth(PyThreadState *tstate);

/* PyGILState */

/* Helper/diagnostic function - return 1 if the current thread
   currently holds the GIL, 0 otherwise.

   The function returns 1 if _PyGILState_check_enabled is non-zero. */
PyAPI_FUNC(int) PyGILState_Check(void);

/* Get the single PyInterpreterState used by this process' GILState
   implementation.

   This function doesn't check for error. Return NULL before _PyGILState_Init()
   is called and after _PyGILState_Fini() is called.

   See also _PyInterpreterState_Get() and _PyInterpreterState_GET(). */
PyAPI_FUNC(PyInterpreterState *) _PyGILState_GetInterpreterStateUnsafe(void);

/* The implementation of sys._current_frames()  Returns a dict mapping
   thread id to that thread's current frame.
*/
PyAPI_FUNC(PyObject *) _PyThread_CurrentFrames(void);


/* Routines for advanced debuggers, requested by David Beazley.
   Don't use unless you know what you are doing! */
PyAPI_FUNC(PyInterpreterState *) PyInterpreterState_Main(void);
PyAPI_FUNC(PyInterpreterState *) PyInterpreterState_Head(void);
PyAPI_FUNC(PyInterpreterState *) PyInterpreterState_Next(PyInterpreterState *);
PyAPI_FUNC(PyThreadState *) PyInterpreterState_ThreadHead(PyInterpreterState *);
PyAPI_FUNC(PyThreadState *) PyThreadState_Next(PyThreadState *);
PyAPI_FUNC(void) PyThreadState_DeleteCurrent(void);
PyAPI_FUNC(int) _PyThreadState_IsRunning(PyThreadState *tstate);

/* Frame evaluation API */

typedef PyObject* (*_PyFrameEvalFunction)(PyThreadState *tstate, PyFrameObject *, int);

PyAPI_FUNC(_PyFrameEvalFunction) _PyInterpreterState_GetEvalFrameFunc(
    PyInterpreterState *interp);
PyAPI_FUNC(void) _PyInterpreterState_SetEvalFrameFunc(
    PyInterpreterState *interp,
    _PyFrameEvalFunction eval_frame);

PyAPI_FUNC(const PyConfig*) _PyInterpreterState_GetConfig(PyInterpreterState *interp);

// Get the configuration of the currrent interpreter.
// The caller must hold the GIL.
PyAPI_FUNC(const PyConfig*) _Py_GetConfig(void);


/* cross-interpreter data */

struct _xid;

// _PyCrossInterpreterData is similar to Py_buffer as an effectively
// opaque struct that holds data outside the object machinery.  This
// is necessary to pass safely between interpreters in the same process.
typedef struct _xid {
    // data is the cross-interpreter-safe derivation of a Python object
    // (see _PyObject_GetCrossInterpreterData).  It will be NULL if the
    // new_object func (below) encodes the data.
    void *data;
    // obj is the Python object from which the data was derived.  This
    // is non-NULL only if the data remains bound to the object in some
    // way, such that the object must be "released" (via a decref) when
    // the data is released.  In that case the code that sets the field,
    // likely a registered "crossinterpdatafunc", is responsible for
    // ensuring it owns the reference (i.e. incref).
    PyObject *obj;
    // interp is the ID of the owning interpreter of the original
    // object.  It corresponds to the active interpreter when
    // _PyObject_GetCrossInterpreterData() was called.  This should only
    // be set by the cross-interpreter machinery.
    //
    // We use the ID rather than the PyInterpreterState to avoid issues
    // with deleted interpreters.  Note that IDs are never re-used, so
    // each one will always correspond to a specific interpreter
    // (whether still alive or not).
    int64_t interp;
    // new_object is a function that returns a new object in the current
    // interpreter given the data.  The resulting object (a new
    // reference) will be equivalent to the original object.  This field
    // is required.
    PyObject *(*new_object)(struct _xid *);
    // free is called when the data is released.  If it is NULL then
    // nothing will be done to free the data.  For some types this is
    // okay (e.g. bytes) and for those types this field should be set
    // to NULL.  However, for most the data was allocated just for
    // cross-interpreter use, so it must be freed when
    // _PyCrossInterpreterData_Release is called or the memory will
    // leak.  In that case, at the very least this field should be set
    // to PyMem_RawFree (the default if not explicitly set to NULL).
    // The call will happen with the original interpreter activated.
    void (*free)(void *);
} _PyCrossInterpreterData;

PyAPI_FUNC(int) _PyObject_GetCrossInterpreterData(PyObject *, _PyCrossInterpreterData *);
PyAPI_FUNC(PyObject *) _PyCrossInterpreterData_NewObject(_PyCrossInterpreterData *);
PyAPI_FUNC(void) _PyCrossInterpreterData_Release(_PyCrossInterpreterData *);

PyAPI_FUNC(int) _PyObject_CheckCrossInterpreterData(PyObject *);

PyAPI_FUNC(long) _PyInterpreterState_GetNumThreads(PyInterpreterState *);

/* cross-interpreter data registry */

typedef int (*crossinterpdatafunc)(PyObject *, struct _xid *);

PyAPI_FUNC(int) _PyCrossInterpreterData_RegisterClass(PyTypeObject *, crossinterpdatafunc);
PyAPI_FUNC(crossinterpdatafunc) _PyCrossInterpreterData_Lookup(PyObject *);

/* Refcounted thread-safe events */

struct _PyEventRC {
    _PyEvent event;
    intptr_t refcnt;
};

PyAPI_FUNC(void) _PyEventRC_Incref(_PyEventRC *);
PyAPI_FUNC(void) _PyEventRC_Decref(_PyEventRC *);
PyAPI_FUNC(_PyEventRC *) _PyEventRC_New(void);

#ifdef __cplusplus
}
#endif
