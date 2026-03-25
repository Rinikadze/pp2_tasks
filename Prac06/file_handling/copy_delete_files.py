import shutil
import os

shutil.copy("sample_data.txt", "copy.txt")
shutil.copy2("sample_data.txt", "backup.txt")

if os.path.exists("copy.txt"):
    os.remove("copy.txt")
if os.path.exists("backup.txt"):
    os.remove("backup.txt")