import os

def list_directory(path):
    print(path + ":")
    names = sorted([name for name in os.listdir(path) if not name.startswith(".")])
    for name in names:
        print(name)
    print()
    for name in names:
        full_path = os.path.join(path, name)
        if os.path.isdir(full_path):
            list_directory(full_path)
 
list_directory(".")