"""Disassembler of Python byte code into mnemonics."""

import sys
import types
import collections
import io

from opcode2 import *
from opcode2 import __all__ as _opcodes_all

__all__ = ["code_info", "dis", "disassemble", "distb", "disco",
           "findlinestarts", "findlabels", "show_code",
           "get_instructions", "Instruction", "Bytecode"] + _opcodes_all
del _opcodes_all

_have_code = (types.MethodType, types.FunctionType2, types.CodeType2,
              classmethod, staticmethod, type)

MAKE_FUNCTION = opmap['MAKE_FUNCTION']
MAKE_FUNCTION_FLAGS = ('defaults', 'kwdefaults', 'annotations', 'closure')

# Meaningless, but cloudpickle imports these (but doesn't use them)
HAVE_ARGUMENT = None
EXTENDED_ARG = None

def _try_compile(source, name):
    """Attempts to compile the given source, first as an expression and
       then as a statement if the first approach fails.

       Utility function to accept strings in functions that otherwise
       expect code objects
    """
    try:
        c = compile(source, name, 'eval')
    except SyntaxError:
        c = compile(source, name, 'exec')
    return c

def dis(x=None, *, file=None, depth=None):
    """Disassemble classes, methods, functions, and other compiled objects.

    With no argument, disassemble the last traceback.

    Compiled objects currently include generator objects, async generator
    objects, and coroutine objects, all of which store their code object
    in a special attribute.
    """
    if x is None:
        distb(file=file)
        return
    # Extract functions from methods.
    if hasattr(x, '__func__'):
        x = x.__func__
    # Extract compiled code objects from...
    if hasattr(x, '__code__'):  # ...a function, or
        x = x.__code__
    elif hasattr(x, 'gi_code'):  #...a generator object, or
        x = x.gi_code
    elif hasattr(x, 'ag_code'):  #...an asynchronous generator object, or
        x = x.ag_code
    elif hasattr(x, 'cr_code'):  #...a coroutine.
        x = x.cr_code
    # Perform the disassembly.
    if hasattr(x, '__dict__'):  # Class or module
        items = sorted(x.__dict__.items())
        for name, x1 in items:
            if isinstance(x1, _have_code):
                print("Disassembly of %s:" % name, file=file)
                try:
                    dis(x1, file=file, depth=depth)
                except TypeError as msg:
                    print("Sorry:", msg, file=file)
                print(file=file)
    elif hasattr(x, 'co_code'): # Code object
        _disassemble_recursive(x, file=file, depth=depth)
    elif isinstance(x, (bytes, bytearray)): # Raw bytecode
        _disassemble_bytes(x, file=file)
    elif isinstance(x, str):    # Source code
        _disassemble_str(x, file=file, depth=depth)
    else:
        raise TypeError("don't know how to disassemble %s objects" %
                        type(x).__name__)

def distb(tb=None, *, file=None):
    """Disassemble a traceback (default: last traceback)."""
    if tb is None:
        try:
            tb = sys.last_traceback
        except AttributeError:
            raise RuntimeError("no last traceback to disassemble") from None
        while tb.tb_next: tb = tb.tb_next
    disassemble(tb.tb_frame.f_code, tb.tb_lasti, file=file)

# The inspect module interrogates this dictionary to build its
# list of CO_* constants. It is also used by pretty_flags to
# turn the co_flags field into a human readable list.
COMPILER_FLAG_NAMES = {
     1: "OPTIMIZED",
     2: "NEWLOCALS",
     4: "VARARGS",
     8: "VARKEYWORDS",
    16: "NESTED",
    32: "GENERATOR",
    64: "NOFREE",
   128: "COROUTINE",
   256: "ITERABLE_COROUTINE",
   512: "ASYNC_GENERATOR",
}

def pretty_flags(flags):
    """Return pretty representation of code flags."""
    names = []
    for i in range(32):
        flag = 1<<i
        if flags & flag:
            names.append(COMPILER_FLAG_NAMES.get(flag, hex(flag)))
            flags ^= flag
            if not flags:
                break
    else:
        names.append(hex(flags))
    return ", ".join(names)

def _get_code_object(x):
    """Helper to handle methods, compiled or raw code objects, and strings."""
    # Extract functions from methods.
    if hasattr(x, '__func__'):
        x = x.__func__
    # Extract compiled code objects from...
    if hasattr(x, '__code__'):  # ...a function, or
        x = x.__code__
    elif hasattr(x, 'gi_code'):  #...a generator object, or
        x = x.gi_code
    elif hasattr(x, 'ag_code'):  #...an asynchronous generator object, or
        x = x.ag_code
    elif hasattr(x, 'cr_code'):  #...a coroutine.
        x = x.cr_code
    # Handle source code.
    if isinstance(x, str):
        x = _try_compile(x, "<disassembly>")
    # By now, if we don't have a code object, we can't disassemble x.
    if hasattr(x, 'co_code'):
        return x
    raise TypeError("don't know how to disassemble %s objects" %
                    type(x).__name__)

def code_info(x):
    """Formatted details of methods, functions, or code."""
    return _format_code_info(_get_code_object(x))

def _format_code_info(co):
    lines = []
    lines.append("Name:              %s" % co.co_name)
    lines.append("Filename:          %s" % co.co_filename)
    lines.append("Argument count:    %s" % co.co_argcount)
    lines.append("Positional-only arguments: %s" % co.co_posonlyargcount)
    lines.append("Kw-only arguments: %s" % co.co_kwonlyargcount)
    lines.append("Number of locals:  %s" % co.co_nlocals)
    lines.append("Stack size:        %s" % (co.co_stacksize))
    lines.append("Flags:             %s" % pretty_flags(co.co_flags))
    if co.co_consts:
        lines.append("Constants:")
        for i_c in enumerate(co.co_consts):
            lines.append("%4d: %r" % i_c)
    if co.co_names:
        lines.append("Names:")
        for i_n in enumerate(co.co_names):
            lines.append("%4d: %s" % i_n)
    if co.co_varnames:
        lines.append("Variable names:")
        for i_n in enumerate(co.co_varnames):
            lines.append("%4d: %s" % i_n)
    if co.co_freevars:
        lines.append("Free variables:")
        for i_n in enumerate(co.co_freevars):
            lines.append("%4d: %s" % i_n)
    if co.co_cellvars:
        lines.append("Cell variables:")
        for i_n in enumerate(co.co_cellvars):
            lines.append("%4d: %s" % i_n)
    return "\n".join(lines)

def show_code(co, *, file=None):
    """Print details of methods, functions, or code to *file*.

    If *file* is not provided, the output is printed on stdout.
    """
    print(code_info(co), file=file)

_Instruction = collections.namedtuple("_Instruction",
     "opname opcode imm argval argrepr offset starts_line is_jump_target")

_Instruction.opname.__doc__ = "Human readable name for operation"
_Instruction.opcode.__doc__ = "Numeric code for operation"
_Instruction.imm.__doc__ = "Immediate arguments"
_Instruction.argval.__doc__ = "Resolved arg value (if known), otherwise same as arg"
_Instruction.argrepr.__doc__ = "Human readable description of operation argument"
_Instruction.offset.__doc__ = "Start index of operation within bytecode sequence"
_Instruction.starts_line.__doc__ = "Line started by this opcode (if any), otherwise None"
_Instruction.is_jump_target.__doc__ = "True if other code jumps to here, otherwise False"

_OPNAME_WIDTH = 20
_OPARG_WIDTH = 5

class Instruction(_Instruction):
    """Details for a bytecode operation

       Defined fields:
         opname - human readable name for operation
         opcode - numeric code for operation
         arg - numeric argument to operation (if any), otherwise None
         argval - resolved arg value (if known), otherwise same as arg
         argrepr - human readable description of operation argument
         offset - start index of operation within bytecode sequence
         starts_line - line started by this opcode (if any), otherwise None
         is_jump_target - True if other code jumps to here, otherwise False
    """

    def _disassemble(self, lineno_width=3, mark_as_current=False, offset_width=4):
        """Format instruction details for inclusion in disassembly output

        *lineno_width* sets the width of the line number field (0 omits it)
        *mark_as_current* inserts a '-->' marker arrow as part of the line
        *offset_width* sets the width of the instruction offset field
        """
        fields = []
        # Column: Source code line number
        if lineno_width:
            if self.starts_line is not None:
                lineno_fmt = "%%%dd" % lineno_width
                fields.append(lineno_fmt % self.starts_line)
            else:
                fields.append(' ' * lineno_width)
        # Column: Current instruction indicator
        if mark_as_current:
            fields.append('-->')
        else:
            fields.append('   ')
        # Column: Jump target marker
        if self.is_jump_target:
            fields.append('>>')
        else:
            fields.append('  ')
        # Column: Instruction offset from start of code sequence
        fields.append(repr(self.offset).rjust(offset_width))
        # Column: Opcode name
        fields.append(self.opname.ljust(_OPNAME_WIDTH))
        # Column: Opcode argument
        args = ' '.join(map(str, self.imm))
        if args != '':
            fields.append(args.rjust(_OPARG_WIDTH))
            if self.argrepr:
                fields.append('(' + self.argrepr + ')')
        return ' '.join(fields).rstrip()


def get_instructions(x, *, first_line=None):
    """Iterator for the opcodes in methods, functions or code

    Generates a series of Instruction named tuples giving the details of
    each operations in the supplied code.

    If *first_line* is not None, it indicates the line number that should
    be reported for the first source line in the disassembled code.
    Otherwise, the source line information (if any) is taken directly from
    the disassembled code object.
    """
    co = _get_code_object(x)
    cell_names = [] # FIXME(sgross): # co.co_cellvars + co.co_freevars
    linestarts = dict(findlinestarts(co))
    if first_line is not None:
        line_offset = first_line - co.co_firstlineno
    else:
        line_offset = 0
    return _get_instructions_bytes(co.co_code, co.co_varnames,
                                   co.co_consts, cell_names, linestarts,
                                   line_offset)

def _get_const_info(const_index, const_list):
    """Helper to get optional details about const references

       Returns the dereferenced constant and its repr if the constant
       list is defined.
       Otherwise returns the constant index and its repr().
    """
    argval = const_index
    if const_list is not None:
        argval = const_list[const_index]
    return argval, repr(argval)

def _get_name_info(name_index, name_list):
    """Helper to get optional details about named references

       Returns the dereferenced name as both value and repr if the name
       list is defined.
       Otherwise returns the name index and its repr().
    """
    argval = name_index
    if name_list is not None:
        argval = name_list[name_index]
        argrepr = argval
    else:
        argrepr = repr(argval)
    return argval, argrepr


def _get_instructions_bytes(code, varnames=None, constants=None,
                            cells=None, linestarts=None, line_offset=0):
    """Iterate over the instructions in a bytecode string.

    Generates a sequence of Instruction namedtuples giving the details of each
    opcode.  Additional information about the code's runtime environment
    (e.g. variable names, constants) can be specified using optional
    arguments.

    """
    def format_reg(reg):
        if varnames is None or reg < len(varnames):
            argval, argrepr = _get_name_info(reg, varnames)
        else:
            argrepr = '.t' + str(reg - len(varnames))
        return argrepr

    def get_const(idx):
        return _get_const_info(idx, constants)[1]

    def get_str(idx):
        return _get_const_info(idx, constants)[0]

    def get_repr(bytecode, *imm):
        argvals = []
        argreprs = []

        for arg, fmt in zip(imm, bytecode.imm):
            argval = arg
            argrepr = None
            if fmt == 'jump':
                argval = offset + (arg if arg <= 0x7FFF else arg - 0x10000)
                argrepr = "to " + repr(argval)
            elif fmt == 'str' or fmt == 'const':
                argval, argrepr = _get_const_info(arg, constants)
            elif fmt == 'cell':
                argval, argrepr = _get_name_info(arg, cells)
            elif fmt == 'reg' or fmt == 'base':
                argrepr = format_reg(arg)
            elif fmt == 'intrinsic':
                argrepr = intrinsics[arg].name
            else:
                argrepr = str(argval)

            argvals.append(argval)
            argreprs.append(argrepr)

        if bytecode.name == 'CALL_FUNCTION':
            argrepr = f'{format_reg(imm[0])} to {format_reg(imm[0]+imm[1])}'
        elif bytecode.name == 'LOAD_ATTR':
            argrepr = f"{argreprs[0]}.{argreprs[1]}"
        elif bytecode.name == 'STORE_ATTR':
            argrepr = f"{argreprs[0]}.{argreprs[1]}=acc"
        elif bytecode.name == 'STORE_SUBSCR':
            argrepr = f"{argreprs[0]}[{argreprs[1]}]=acc"
        elif bytecode.name == 'BINARY_SUBSCR':
            argrepr = f"{argreprs[0]}[acc]"
        elif bytecode.name == 'MOVE' or bytecode.name == 'COPY':
            argrepr = f"{argreprs[0]} <- {argreprs[1]}"
        elif bytecode.name == 'UNPACK':
            argrepr = f'{argreprs[0]} argcnt={argreprs[1]} after={argreprs[2]}'
        else:
            argrepr = '; '.join(argreprs)

        if len(argvals) == 0:
            argval = None
        elif len(argvals) == 1:
            argval = argvals[0]
        else:
            argval = tuple(argvals)

        return argval, argrepr


    labels = findlabels(code)
    starts_line = None
    for offset, op, *imm in _unpack_opargs(code):
        if linestarts is not None:
            starts_line = linestarts.get(offset, None)
            if starts_line is not None:
                starts_line += line_offset
        is_jump_target = offset in labels
        bytecode = opcodes[op]
        argval, argrepr = get_repr(bytecode, *imm)
        yield Instruction(opname[op], op,
                          imm, argval, argrepr,
                          offset, starts_line, is_jump_target)

def disassemble(co, lasti=-1, *, file=None):
    """Disassemble a code object."""
    cell_names = co.co_cellvars + co.co_freevars
    linestarts = dict(findlinestarts(co))
    _disassemble_bytes(co.co_code, lasti, co.co_varnames,
                       co.co_consts, cell_names, linestarts, co.co_cell2reg,
                       co.co_free2reg, co.co_exc_handlers, file=file)

def _disassemble_recursive(co, *, file=None, depth=None):
    disassemble(co, file=file)
    if depth is None or depth > 0:
        if depth is not None:
            depth = depth - 1
        for x in co.co_consts:
            if hasattr(x, 'co_code'):
                print(file=file)
                print("Disassembly of %r:" % (x,), file=file)
                _disassemble_recursive(x, file=file, depth=depth)

def _disassemble_bytes(code, lasti=-1, varnames=None, constants=None,
                       cells=None, linestarts=None, cell2reg=None,
                       free2reg=None, exc_handlers=None,
                       *, file=None, line_offset=0):
    # Omit the line number column entirely if we have no line number info
    show_lineno = linestarts is not None
    if show_lineno:
        maxlineno = max(linestarts.values()) + line_offset
        if maxlineno >= 1000:
            lineno_width = len(str(maxlineno))
        else:
            lineno_width = 3
    else:
        lineno_width = 0
    maxoffset = len(code) - 2
    if maxoffset >= 10000:
        offset_width = len(str(maxoffset))
    else:
        offset_width = 4
    for instr in _get_instructions_bytes(code, varnames,
                                         constants, cells, linestarts,
                                         line_offset=line_offset):
        new_source_line = (show_lineno and
                           instr.starts_line is not None and
                           instr.offset > 0)
        if new_source_line:
            print(file=file)
        is_current_instr = instr.offset == lasti
        print(instr._disassemble(lineno_width, is_current_instr, offset_width),
              file=file)
    if cell2reg:
        print(' ' * 2 + f'Cell variables: {list(cell2reg)}', file=file)
    if free2reg:
        print(' ' * 2 + f'Free variables: {list(free2reg)}', file=file)
    if exc_handlers:
        print(' ' * 2 + f'Exception handlers ({len(exc_handlers)}):', file=file)
        print(f'    start  ->  (handler,  end)', file=file)
        for start, handler, end, reg in exc_handlers:
            print(f'     {start:4d}  ->      {handler:4d}, {end:4d}  [reg={reg}]', file=file)

def _disassemble_str(source, **kwargs):
    """Compile the source string, then disassemble the code object."""
    _disassemble_recursive(_try_compile(source, '<dis>'), **kwargs)

disco = disassemble                     # XXX For backwards compatibility

def signed(x):
    return x if x < 32768 else (x - 65536)

def decode_imm(code, offset, bytecode, wide):
    sizes = {
        'imm16': 2,
        'jump': 4 if wide else 2,
    }
    offset += 1
    if wide:
        offset += 1
    for imm in bytecode.imm:
        signed = (imm == 'jump')
        size = sizes.get(imm, 4 if wide else 1)
        yield int.from_bytes(code[offset:offset+size], 'little', signed=signed)
        offset += size


def _unpack_opargs(code):
    extended_arg = 0
    i = 0
    WIDE = opmap['WIDE']
    while i < len(code):
        wide = False
        op = code[i]
        bytecode = opcodes[op]
        if bytecode is None:
            raise RuntimeError(f'bad opcode {op}')

        if bytecode == WIDE:
            wide = True
            op = code[i+1]
            bytecode = opcodes[op]
            size = bytecode.wide_size
        else:
            size = bytecode.size

        imm = list(decode_imm(code, i, bytecode, wide))
        yield (i, op, *imm)
        i += size

def findlabels(code):
    """Detect all offsets in a byte code which are jump targets.

    Return the list of offsets.

    """
    labels = []
    for offset, op, *imm in _unpack_opargs(code):
        if opcodes[op].is_jump():
            label = offset + imm[-1]
            if label not in labels:
                labels.append(label)
    return labels

def findlinestarts(code):
    """Find the offsets in a byte code which are start of lines in the source.

    Generate pairs (offset, lineno) as described in Python/compile.c.

    """
    byte_increments = code.co_lnotab[0::2]
    line_increments = code.co_lnotab[1::2]
    bytecode_len = len(code.co_code)

    lastlineno = None
    lineno = code.co_firstlineno
    addr = 0
    for byte_incr, line_incr in zip(byte_increments, line_increments):
        if byte_incr:
            if lineno != lastlineno:
                yield (addr, lineno)
                lastlineno = lineno
            addr += byte_incr
            if addr >= bytecode_len:
                # The rest of the lnotab byte offsets are past the end of
                # the bytecode, so the lines were optimized away.
                return
        if line_incr >= 0x80:
            # line_increments is an array of 8-bit signed integers
            line_incr -= 0x100
        lineno += line_incr
    if lineno != lastlineno:
        yield (addr, lineno)

class Bytecode:
    """The bytecode operations of a piece of code

    Instantiate this with a function, method, other compiled object, string of
    code, or a code object (as returned by compile()).

    Iterating over this yields the bytecode operations as Instruction instances.
    """
    def __init__(self, x, *, first_line=None, current_offset=None):
        self.codeobj = co = _get_code_object(x)
        if first_line is None:
            self.first_line = co.co_firstlineno
            self._line_offset = 0
        else:
            self.first_line = first_line
            self._line_offset = first_line - co.co_firstlineno
        self._cell_names = co.co_cellvars + co.co_freevars
        self._linestarts = dict(findlinestarts(co))
        self._original_object = x
        self.current_offset = current_offset

    def __iter__(self):
        co = self.codeobj
        return _get_instructions_bytes(co.co_code, co.co_varnames,
                                       co.co_consts, self._cell_names,
                                       self._linestarts,
                                       line_offset=self._line_offset)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__,
                                 self._original_object)

    @classmethod
    def from_traceback(cls, tb):
        """ Construct a Bytecode from the given traceback """
        while tb.tb_next:
            tb = tb.tb_next
        return cls(tb.tb_frame.f_code, current_offset=tb.tb_lasti)

    def info(self):
        """Return formatted information about the code object."""
        return _format_code_info(self.codeobj)

    def dis(self):
        """Return a formatted view of the bytecode operations."""
        co = self.codeobj
        if self.current_offset is not None:
            offset = self.current_offset
        else:
            offset = -1
        with io.StringIO() as output:
            _disassemble_bytes(co.co_code, varnames=co.co_varnames,
                               constants=co.co_consts,
                               cells=self._cell_names,
                               linestarts=self._linestarts,
                               line_offset=self._line_offset,
                               cell2reg=co.co_cell2reg,
                               free2reg=co.co_free2reg,
                               exc_handlers=co.co_exc_handlers,
                               file=output,
                               lasti=offset)
            return output.getvalue()


def _test():
    """Simple test program to disassemble a file."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=argparse.FileType('rb'), nargs='?', default='-')
    args = parser.parse_args()
    with args.infile as infile:
        source = infile.read()
    code = compile(source, args.infile.name, "exec")
    dis(code)

if __name__ == "__main__":
    _test()
