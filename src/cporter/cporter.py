import ctypes
import re
import os
import subprocess
import time
import timeit
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, TypeVar, Type

T = TypeVar("T")


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
            "unsigned char": ctypes.c_ubyte,
            "bool": ctypes.c_bool,
            "void": None,
        }

    # Compiles and loads the library with the given name
    def add_library(self, lib_name: str) -> None:
        self.compile_library(self, lib_name)
        self.load_library(lib_name)

    def set_library_path(self, lib_path: str) -> None:
        self.lib_path = lib_path

    # Compiles the C library into a shared object (.so) file
    @staticmethod
    def compile_library(self, lib_name: str) -> None:
        result = subprocess.run(
            ["gcc", "-shared", "-o", f"{lib_name}.so", f"{self.lib_path}/{lib_name}.c"],
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to compile library '{lib_name}'. GCC returned the following error:\n{result.stderr.decode('utf-8')}"
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
    def get_function(self, lib_name: str, func_name: str) -> Callable[..., Any]:
        lib = self.libraries.get(lib_name)
        if lib is None:
            raise ValueError(f"Library '{lib_name}' not found.")

        argtypes, restype = self.get_function_types(lib_name, func_name)
        # get our callable function from ctypes
        func = lib.__getattr__(func_name)
        # Filter out None values
        func.argtypes = [t for t in argtypes if t is not None]
        func.restype = restype
        return func

    # Reads the C source code to determine the argument and return types of the specified function
    def get_function_types(
        self, lib_name: str, func_name: str
    ) -> Tuple[List[Optional[Type[ctypes._SimpleCData]]], Optional[Type[ctypes._SimpleCData]]]:

        with open(f"examples/lib/{lib_name}.c", "r") as f:
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
        return func(*args)

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
