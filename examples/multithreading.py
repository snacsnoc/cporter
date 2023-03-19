import sys
import os
import ctypes

# Add the 'src' directory to the Python import path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from concurrent.futures import ThreadPoolExecutor, as_completed
from cporter import CPorter

# Create a CPorter instance and load the library
cporter = CPorter()
cporter.set_library_path("examples/lib")
cporter.add_library("array")

# Define the input array
A_py = [i for i in range(1, 10001)]
n = len(A_py)

# Convert Python list to a ctypes array
A = (ctypes.c_int * n)(*A_py)


def python_sum_of_squares(arr):
    return sum(x * x for x in arr)

# Execute the C and Python functions concurrently using a thread pool
with ThreadPoolExecutor() as executor:
    # Submit the tasks to the thread pool
    c_futures = [executor.submit(cporter.profile_function, "array", "sum_of_squares", A, n) for _ in range(10)]
    py_futures = [executor.submit(cporter.profile_python_function, python_sum_of_squares, A) for _ in range(10)]

    # Wait for the tasks to complete and retrieve the results
    c_results = [future.result() for future in as_completed(c_futures)]
    py_results = [future.result() for future in as_completed(py_futures)]

# Process the results as needed
for i, (c_result, py_result) in enumerate(zip(c_results, py_results)):
    print(f"Task {i + 1}:")
    print(f"C Result: {c_result[0]}, Time: {c_result[1]} seconds")
    print(f"Python Result: {py_result[0]}, Time: {py_result[1]} seconds")
