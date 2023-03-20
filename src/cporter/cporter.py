import ctypes
import re
import os
import subprocess
import time
import timeit
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, TypeVar, Type
import shutil

T = TypeVar("T")


# Simplify C memory management by automatically deallocate memory when the objects are garbage collected
class CStringWrapper:
    def __init__(self, value: bytes):
        self._as_parameter_ = ctypes.create_string_buffer(value)

    def __del__(self):
        self.function_to_free_memory(self._as_parameter_)

    @staticmethod
    def function_to_free_memory(c_string_buffer):
        # We are assuming the user used malloc()
        libc = ctypes.CDLL(ctypes.util.find_library("c"))
        libc.free.argtypes = [ctypes.c_void_p]
        libc.free.restype = None
        libc.free(ctypes.addressof(c_string_buffer))


class CFunctionWrapper:
    # _argtypes: CData isn't callable ( but _SimpleCData is)
    # we call CFunctionWrapper with a ctype._CData list, so Type[Any] is used to get around this
    #
    def __init__(
        self,
        func: Callable[..., Any],
        argtypes: List[Type[Any]],
        restype: Optional[Type[ctypes._SimpleCData]],
        doc: Optional[str] = None,
    ):
        self.func = func
        self.argtypes = argtypes
        self.restype = restype
        self.__doc__ = doc

    def __call__(self, *args: Any) -> Any:
        return self.func(*args)


class CPorter:
    def __init__(self) -> None:
        self.libraries: Dict[str, ctypes.CDLL] = {}
        self.type_map: Dict[str, Union[None, type[ctypes._SimpleCData]]] = {
            "int": ctypes.c_int,
            "unsigned int": ctypes.c_uint,
            "long": ctypes.c_long,
            "unsigned long": ctypes.c_ulong,
            "long long": ctypes.c_longlong,
            "unsigned long long": ctypes.c_ulonglong,
            "short": ctypes.c_short,
            "unsigned short": ctypes.c_ushort,
            "float": ctypes.c_float,
            "double": ctypes.c_double,
            "long double": ctypes.c_longdouble,
            "char": ctypes.c_char,
            "char*": ctypes.c_char_p,
            "unsigned char": ctypes.c_ubyte,
            "bool": ctypes.c_bool,
            "void": None,
            "void*": ctypes.c_void_p,
            "size_t": ctypes.c_size_t,
            "ptrdiff_t": ctypes.c_ptrdiff_t,
            "intptr_t": ctypes.c_intptr_t,
            "uintptr_t": ctypes.c_uintptr_t,
            "int8_t": ctypes.c_int8,
            "uint8_t": ctypes.c_uint8,
            "int16_t": ctypes.c_int16,
            "uint16_t": ctypes.c_uint16,
            "int32_t": ctypes.c_int32,
            "uint32_t": ctypes.c_uint32,
            "int64_t": ctypes.c_int64,
            "uint64_t": ctypes.c_uint64,
        }

    # Compiles and loads the library with the given name
    def add_library(self, lib_name: str) -> None:
        self.compile_library(self, lib_name)
        self.load_library(lib_name)

    def set_library_path(self, lib_path: str) -> None:
        self.lib_path = lib_path

    # Compiles the C library into a shared object (.so) file
    # TODO: add support to .dll
    @staticmethod
    def compile_library(self, lib_name: str) -> None:
        # Check if the CC environment variable is set
        compiler = os.environ.get("CC")

        if compiler is None:
            # Check if 'gcc' is available
            if shutil.which("gcc"):
                compiler = "gcc"
            # Check if 'clang' is available
            elif shutil.which("clang"):
                compiler = "clang"
            else:
                raise RuntimeError(
                    "No suitable C compiler found. Please ensure that either 'gcc' or 'clang' is installed and available in the PATH."
                )

        result = subprocess.run(
            [
                compiler,
                "-shared",
                "-o",
                f"{lib_name}.so",
                f"{self.lib_path}/{lib_name}.c",
            ],
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to compile library '{lib_name}'. {compiler} returned the following error:\n{result.stderr.decode('utf-8')}"
            )

    # Loads the compiled C library as a shared object using ctypes
    def load_library(self, lib_name: str) -> None:
        shared_obj_path = f"./{lib_name}.so"
        if not os.path.isfile(shared_obj_path):
            raise FileNotFoundError(
                f"Shared object file '{shared_obj_path}' not found. Please make sure the library is compiled."
            )

        try:
            self.libraries[lib_name] = ctypes.CDLL(shared_obj_path)
        except OSError as e:
            raise RuntimeError(
                f"Failed to load library '{lib_name}'. ctypes raised the following error:\n{str(e)}"
            )

    # Retrieves the function from the specified library and configures its argument and return types
    def get_function(self, lib_name: str, func_name: str) -> CFunctionWrapper:
        lib = self.libraries.get(lib_name)
        if lib is None:
            raise ValueError(f"Library '{lib_name}' not found.")

        argtypes, restype = self.get_function_types(lib_name, func_name)
        # get our callable function from ctypes
        func = lib.__getattr__(func_name)
        # Filter out None values
        func.argtypes = [t for t in argtypes if t is not None]
        func.restype = restype
        # Attach the function documentation as a docstring
        documentation = self.get_function_documentation(lib_name, func_name)
        if documentation:
            func.__doc__ = documentation

        # Wrap the ctypes function object as an instance of CFunctionWrapper
        c_function = CFunctionWrapper(
            func=func, argtypes=func.argtypes, restype=func.restype, doc=func.__doc__
        )
        return c_function

    # Reads the C source code to determine the argument and return types of the specified function
    def get_function_types(
        self, lib_name: str, func_name: str
    ) -> Tuple[
        List[Optional[Type[ctypes._SimpleCData]]], Optional[Type[ctypes._SimpleCData]]
    ]:

        with open(f"{self.lib_path}/{lib_name}.c", "r") as f:
            c_code = f.read()

        pattern = r"(\w+)\s+" + re.escape(func_name) + r"\s*\((?:([\w\s,*]+))?\)"
        match = re.search(pattern, c_code)

        if match:
            return_type, arg_types_str = match.groups()
            if arg_types_str is None:
                arg_types = []
            else:
                arg_types = [s.strip() for s in arg_types_str.split(",")]
            return [
                self.type_map[t] for t in arg_types if t in self.type_map
            ], self.type_map.get(return_type)

        raise ValueError(f"Function '{func_name}' not found in '{lib_name}'.")

    def execute_function(self, lib_name: str, func_name: str, *args) -> Any:
        func = self.get_function(lib_name, func_name)

        # Convert Python types to ctypes equivalents
        converted_args = []
        for i, (arg, ctype) in enumerate(zip(args, func.argtypes)):
            if ctype == ctypes.c_char_p:
                converted_arg = CStringWrapper(arg)
            elif not isinstance(arg, ctype):
                try:
                    converted_arg = ctype(arg)
                except Exception as e:
                    raise TypeError(
                        f"Argument {i} of function '{func_name}' in library '{lib_name}' "
                        f"must be of type '{ctype.__name__}', but received '{type(arg).__name__}'."
                    ) from e
            else:
                converted_arg = arg
            converted_args.append(converted_arg)

        # Call the function with converted arguments
        result = func(*converted_args)

        # Check return type
        if func.restype is not None:
            if not isinstance(result, func.restype):
                python_equivalent = type(func.restype().value)
                if not isinstance(result, python_equivalent):
                    raise TypeError(
                        f"Return value of function '{func_name}' in library '{lib_name}' "
                        f"must be of type '{func.restype.__name__}', but received '{type(result).__name__}'."
                    )

        return result

    # Profile a C function to retrieve total execution time
    def profile_function(
        self, lib_name: str, func_name: str, *args
    ) -> Tuple[Any, float]:
        start_time = time.perf_counter()
        result = self.execute_function(lib_name, func_name, *args)
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time
        return result, elapsed_time

    def profile_python_function(
        self, func: Callable[..., T], *args: Any
    ) -> Tuple[T, float]:
        start_time = timeit.default_timer()
        result = func(*args)
        elapsed_time = timeit.default_timer() - start_time
        return result, elapsed_time

    def get_function_documentation(
        self, lib_name: str, func_name: str
    ) -> Optional[str]:
        with open(f"{self.lib_path}/{lib_name}.c", "r") as f:
            c_code = f.read()

        # Match comments preceding function definitions
        pattern = r"(?s)(/\*[\s\S]*?\*/\s*)?(\w+)\s+" + re.escape(func_name) + r"\s*\("
        match = re.search(pattern, c_code)

        if match:
            comment = match.group(1)
            if comment is not None:
                # Remove comment delimiters and leading/trailing whitespace
                documentation = re.sub(r"^\s*/\*|\*/\s*$", "", comment).strip()
                return documentation

        return None
