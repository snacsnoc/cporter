# CPorter
CPorter is a statically-typed Python library using ctypes that makes it easy to integrate C code into your Python projects. 
It simplifies the process of compiling, loading, and calling C functions from Python by automatically handling C types and providing performance profiling utilities.


## Features
* Compile and load C libraries with a single function call
* Automatic C function type detection and handling
* Simplified function calling syntax in Python
* Multithreading support
* Performance profiling for both C and Python functions

## Installation
To use CPorter in your project, simply clone the repository and import the cporter module.

```
git clone https://github.com/snacsnoc/cporter.git
```
## Usage
Here's an example of using CPorter to load and call a C function:

```python
from cporter import CPorter

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
from cporter import CPorter

cporter = CPorter()
cporter.set_library_path("lib")
cporter.add_library("my_library")

result, elapsed_time = cporter.profile_function("my_library", "my_function", arg1, arg2)
print(f"Elapsed time: {elapsed_time:.6f} seconds")
```
For profiling Python functions, you can use the `profile_python_function` method:

```python
from cporter import CPorter

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
from cporter import CPorter

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
## Examples
Call two difference functions with arguments example: `python examples/run.py`

Multithreading example: `python examples/multithreading.py`

## Contributing
Pull requests are always welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
GNU GPLv3
