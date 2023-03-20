from cporter.cporter import CPorter, CStringWrapper

# Initialize CPorter
c_porter = CPorter()

# Set the library path to the lib directory
# Path can be relative or absolute
c_porter.set_library_path("examples/lib")

# Compile and load the library
c_porter.add_library("string_lib")

# Get the 'create_string' function from the 'string_lib' library
create_string_func = c_porter.get_function("string_lib", "create_string")

# Execute the 'create_string' function and wrap the result in CStringWrapper
input_string = "Hello, world!"
cstring = CStringWrapper(create_string_func(input_string))
print(f"Allocated string: {cstring.value}")

# Get the 'free_string' function from the 'my_string_lib' library
free_string_func = c_porter.get_function("string_lib", "free_string")

# Release the memory of the CStringWrapper instance
cstring.free_memory(free_string_func)
