import sys
import os

# Add the 'src' directory to the Python import path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from cporter import CPorter

ffi_test = CPorter()

ffi_test.set_library_path("examples/lib")
# Add the 'main' and 'fib' library
ffi_test.add_library("main")
ffi_test.add_library("fib")

# Get the function from the compiled library
example_function = ffi_test.get_function("main", "example_function_name")
fib_n = ffi_test.get_function("fib", "fibonacci_iterative")

# Call the function with arguments
result = example_function(42)
print("Result:", result)

# Calculate the nth Fibonacci number
fib_result = fib_n(90)
print("Fibonacci nth number:", fib_result)