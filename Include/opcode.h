/* Auto-generated by Tools/scripts/generate_opcode_h.py from Lib/opcode.py */
#ifndef Py_OPCODE_H
#define Py_OPCODE_H
#ifdef __cplusplus
extern "C" {
#endif


// Instruction opcodes for compiled code
//    name                   opcode   size   wide_size
#define OPCODE_LIST(_) \
    _(CLEAR_ACC,                  1,     1,      2) \
    _(CLEAR_FAST,                 2,     2,      6) \
    _(ALIAS,                      3,     3,     10) \
    _(COPY,                       4,     3,     10) \
    _(MOVE,                       5,     3,     10) \
    _(FUNC_HEADER,                6,     2,      6) \
    _(METHOD_HEADER,              7,     1,      2) \
    _(CFUNC_HEADER,               9,     1,      2) \
    _(CFUNC_HEADER_NOARGS,       10,     1,      2) \
    _(CFUNC_HEADER_O,            11,     1,      2) \
    _(CMETHOD_NOARGS,            12,     1,      2) \
    _(CMETHOD_O,                 13,     1,      2) \
    _(FUNC_TPCALL_HEADER,        14,     1,      2) \
    _(UNARY_POSITIVE,            15,     1,      2) \
    _(UNARY_NEGATIVE,            16,     1,      2) \
    _(UNARY_NOT,                 17,     1,      2) \
    _(UNARY_NOT_FAST,            18,     1,      2) \
    _(UNARY_INVERT,              19,     1,      2) \
    _(BINARY_MATRIX_MULTIPLY,    20,     2,      6) \
    _(BINARY_POWER,              21,     2,      6) \
    _(BINARY_MULTIPLY,           22,     2,      6) \
    _(BINARY_MODULO,             23,     2,      6) \
    _(BINARY_ADD,                24,     2,      6) \
    _(BINARY_SUBTRACT,           25,     2,      6) \
    _(BINARY_SUBSCR,             26,     2,      6) \
    _(BINARY_FLOOR_DIVIDE,       27,     2,      6) \
    _(BINARY_TRUE_DIVIDE,        28,     2,      6) \
    _(BINARY_LSHIFT,             29,     2,      6) \
    _(BINARY_RSHIFT,             30,     2,      6) \
    _(BINARY_AND,                31,     2,      6) \
    _(BINARY_XOR,                32,     2,      6) \
    _(BINARY_OR,                 33,     2,      6) \
    _(IS_OP,                     34,     2,      6) \
    _(CONTAINS_OP,               35,     2,      6) \
    _(COMPARE_OP,                36,     3,     10) \
    _(INPLACE_FLOOR_DIVIDE,      37,     2,      6) \
    _(INPLACE_TRUE_DIVIDE,       38,     2,      6) \
    _(INPLACE_ADD,               39,     2,      6) \
    _(INPLACE_SUBTRACT,          40,     2,      6) \
    _(INPLACE_MULTIPLY,          41,     2,      6) \
    _(INPLACE_LSHIFT,            42,     2,      6) \
    _(INPLACE_RSHIFT,            43,     2,      6) \
    _(INPLACE_AND,               44,     2,      6) \
    _(INPLACE_XOR,               45,     2,      6) \
    _(INPLACE_OR,                46,     2,      6) \
    _(INPLACE_MODULO,            47,     2,      6) \
    _(INPLACE_MATRIX_MULTIPLY,   48,     2,      6) \
    _(INPLACE_POWER,             49,     2,      6) \
    _(LOAD_FAST,                 50,     2,      6) \
    _(LOAD_NAME,                 51,     3,     10) \
    _(LOAD_CONST,                52,     2,      6) \
    _(LOAD_ATTR,                 53,     4,     14) \
    _(LOAD_GLOBAL,               54,     3,     10) \
    _(LOAD_METHOD,               55,     4,     14) \
    _(LOAD_DEREF,                56,     2,      6) \
    _(LOAD_CLASSDEREF,           57,     3,     10) \
    _(STORE_FAST,                58,     2,      6) \
    _(STORE_NAME,                59,     2,      6) \
    _(STORE_ATTR,                60,     3,     10) \
    _(STORE_GLOBAL,              61,     2,      6) \
    _(STORE_SUBSCR,              62,     3,     10) \
    _(STORE_DEREF,               63,     2,      6) \
    _(DELETE_FAST,               64,     2,      6) \
    _(DELETE_NAME,               65,     2,      6) \
    _(DELETE_ATTR,               66,     2,      6) \
    _(DELETE_GLOBAL,             67,     2,      6) \
    _(DELETE_SUBSCR,             68,     2,      6) \
    _(DELETE_DEREF,              69,     2,      6) \
    _(CALL_FUNCTION,             70,     4,      8) \
    _(CALL_FUNCTION_EX,          71,     2,      6) \
    _(CALL_METHOD,               72,     4,      8) \
    _(CALL_INTRINSIC_1,          73,     2,      6) \
    _(CALL_INTRINSIC_N,          74,     4,     14) \
    _(RETURN_VALUE,              75,     1,      2) \
    _(RAISE,                     76,     1,      2) \
    _(YIELD_VALUE,               77,     1,      2) \
    _(YIELD_FROM,                78,     2,      6) \
    _(JUMP,                      79,     3,      6) \
    _(JUMP_IF_FALSE,             80,     3,      6) \
    _(JUMP_IF_TRUE,              81,     3,      6) \
    _(JUMP_IF_NOT_EXC_MATCH,     82,     4,     10) \
    _(POP_JUMP_IF_FALSE,         83,     3,      6) \
    _(POP_JUMP_IF_TRUE,          84,     3,      6) \
    _(GET_ITER,                  85,     2,      6) \
    _(GET_YIELD_FROM_ITER,       86,     2,      6) \
    _(FOR_ITER,                  87,     4,     10) \
    _(IMPORT_NAME,               88,     2,      6) \
    _(IMPORT_FROM,               89,     3,     10) \
    _(IMPORT_STAR,               90,     2,      6) \
    _(BUILD_SLICE,               91,     2,      6) \
    _(BUILD_TUPLE,               92,     3,     10) \
    _(BUILD_LIST,                93,     3,     10) \
    _(BUILD_SET,                 94,     3,     10) \
    _(BUILD_MAP,                 95,     2,      6) \
    _(END_EXCEPT,                96,     2,      6) \
    _(CALL_FINALLY,              97,     4,     10) \
    _(END_FINALLY,               98,     2,      6) \
    _(LOAD_BUILD_CLASS,          99,     1,      2) \
    _(GET_AWAITABLE,            100,     3,     10) \
    _(GET_AITER,                101,     2,      6) \
    _(GET_ANEXT,                102,     2,      6) \
    _(END_ASYNC_WITH,           103,     2,      6) \
    _(END_ASYNC_FOR,            104,     2,      6) \
    _(UNPACK,                   105,     4,     14) \
    _(MAKE_FUNCTION,            106,     2,      6) \
    _(SETUP_WITH,               107,     2,      6) \
    _(END_WITH,                 108,     2,      6) \
    _(SETUP_ASYNC_WITH,         109,     2,      6) \
    _(LIST_EXTEND,              110,     2,      6) \
    _(LIST_APPEND,              111,     2,      6) \
    _(SET_ADD,                  112,     2,      6) \
    _(SET_UPDATE,               113,     2,      6) \
    _(DICT_MERGE,               114,     2,      6) \
    _(DICT_UPDATE,              115,     2,      6) \
    _(SETUP_ANNOTATIONS,        116,     1,      2) \
    _(SET_FUNC_ANNOTATIONS,     117,     2,      6) \
    _(WIDE,                     118,     1,      2)

#define INTRINSIC_LIST(_) \
    _(PyObject_Str,                   1) \
    _(PyObject_Repr,                  2) \
    _(PyObject_ASCII,                 3) \
    _(vm_format_value,                4) \
    _(vm_format_value_spec,           5) \
    _(vm_build_string,                6) \
    _(PyList_AsTuple,                 7) \
    _(vm_raise_assertion_error,       8) \
    _(vm_exc_set_cause,               9) \
    _(vm_print,                      10) \
    _(_PyAsyncGenValueWrapperNew,    11)


enum {
#define OPCODE_NAME(Name, Code, ...) Name = Code,
OPCODE_LIST(OPCODE_NAME)
#undef OPCODE_NAME
};

enum {
#define OPSIZE(Name, Code, Size, ...) OP_SIZE_##Name = Size,
OPCODE_LIST(OPSIZE)
#undef OPSIZE
};

enum {
#define OPSIZE(Name, Code, Size, WideSize) OP_SIZE_WIDE_##Name = WideSize,
OPCODE_LIST(OPSIZE)
#undef OPSIZE
};

enum {
#define INTRINSIC_CODE(Name, Code) Intrinsic_##Name = Code,
INTRINSIC_LIST(INTRINSIC_CODE)
#undef INTRINSIC_CODE
};

#ifdef __cplusplus
}
#endif
#endif /* !Py_OPCODE_H */
