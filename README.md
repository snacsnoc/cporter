# CPorter
[![Mypy check](https://github.com/snacsnoc/cporter/actions/workflows/mypy.yml/badge.svg)](https://github.com/snacsnoc/cporter/actions/workflows/mypy.yml)

CPorter is a Python library using ctypes that makes it easy to integrate C code into your Python projects. 
It simplifies the process of compiling, loading, and calling C functions from Python by automatically handling C types and providing performance profiling utilities.


## Features
* Compile and load C libraries with a single function call
* Automatic C function type detection and handling
* Simplified function calling syntax in Python
* Multithreading support
* Performance profiling for both C and Python functions
* Get C function documentation from source code(/* Text */)
* Automatic memory management for C code allocating memory using malloc (don't rely on this)

## Installation
To use CPorter in your project, install from pip or by cloning.
```bash
pip install -i https://test.pypi.org/simple/ cporter
```
or

```
git clone https://github.com/snacsnoc/cporter.git
```
and add the `src/` to your Python lib path
## Usage
Here's an example of using CPorter to load and call a C function:

```python
from cporter.cporter import CPorter

# Create a CPorter instance and load the library
cporter = CPorter()
cporter.set_library_path("lib")
cporter.add_library("my_library")

# Call the C function
c_function = cporter.get_function("my_library", "my_function")
result = c_function(arg1, arg2)
```

## Profiling
CPorter also supports performance profiling for both C and Python functions. Here's an example of profiling a C function:

```python
from cporter.cporter import CPorter

cporter = CPorter()
cporter.set_library_path("lib")
cporter.add_library("my_library")

result, elapsed_time = cporter.profile_function("my_library", "my_function", arg1, arg2)
print(f"Elapsed time: {elapsed_time:.6f} seconds")
```
For profiling Python functions, you can use the `profile_python_function` method:

```python
from cporter.cporter import CPorter

cporter = CPorter()

def my_python_function(arg1, arg2):
    # Your Python function implementation here
    pass

result, elapsed_time = cporter.profile_python_function(my_python_function, arg1, arg2)
print(f"Elapsed time: {elapsed_time:.6f} seconds")
```
## Multithreading
CPorter supports multithreading to run C and Python functions concurrently. Here's an example of running a C function and a Python function concurrently using a thread pool:

```python
import ctypes
from concurrent.futures import ThreadPoolExecutor, as_completed
from cporter.cporter import CPorter

cporter = CPorter()
cporter.set_library_path("lib")
cporter.add_library("my_library")

# Define your Python function here
def my_python_function(arg1, arg2):
    pass

# Define input arguments for the C and Python functions
arg1, arg2 = 1, 1

# Execute the C and Python functions concurrently using a thread pool
with ThreadPoolExecutor() as executor:
    c_futures = [executor.submit(cporter.execute_c_function, "my_library", "my_function", arg1, arg2) for _ in range(10)]
    py_futures = [executor.submit(my_python_function, arg1, arg2) for _ in range(10)]

    # Wait for the tasks to complete and retrieve the results
    c_results = [future.result() for future in as_completed(c_futures)]
    py_results = [future.result() for future in as_completed(py_futures)]

# Process the results as needed
```

## Function Documentation
CPorter can now extract the docstring for a C function from its source code. If the C function has a docstring in the form of a block comment immediately preceding its declaration, CPorter can parse it and attach the docstring to the corresponding Python-wrapped function. 

Example:
```c
/* Compute the sum of two integers. */
int add(int a, int b) {
    return a + b;
}
```
In Python, you can access the docstring like this:

```python
cporter = CPorter()
# ... Load the library and get the function ...
add_function = cporter.get_function("my_library", "add")
print(add_function.__doc__)
```
This will output:

```python
Compute the sum of two integers.
```

## Automatic Type Checking with ctypes
CPorter automatically handles type checking and conversion for function arguments and return values. 
When calling a C function wrapped by CPorter, you can pass Python values directly, and CPorter will attempt to convert them to the appropriate ctypes equivalents. 
It also checks if the provided values are valid for the expected C types, and raises a helpful error message if there's a type mismatch or an invalid value.

This makes it easier to work with C functions from Python, as you don't need to manually convert Python values to ctypes objects.
```python
cporter = CPorter()
# ... Load the library and get the function ...
add_function = cporter.get_function("my_library", "add")
result = add_function(1, 2)  # You can pass Python values directly
print(result)  # The result is automatically converted back to a Python value

```
## Examples
Call two different functions with arguments example: `python examples/run.py`

Multithreading example: `python examples/multithreading.py`

## Contributing
Pull requests are always welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
GNU GPLv3
