import sys
from xml.etree.ElementInclude import include
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
# build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

includes = ["jinja2.ext"]  # add jinja2.ext here
packages = ["sqlalchemy"]
excludes = ["Tkinter"]
target = Executable(script="main.py", base=base)

build_exe_options = dict(
    includes=includes,
    packages=packages,
    excludes=excludes,
    include_files=["resources/", "templates/", "static/", "app.db"],
)  # folder,relative path. Use tuple like in the single file to set a absolute path.

setup(
    name="Flask App",
    version="0.1",
    description="Flask App",
    copyDependentFiles=True,
    options={"build_exe": build_exe_options},
    executables=[target],
)

# # Copy files

# import os
# import shutil
# import os, shutil


# def copytree(src, dst, symlinks=False, ignore=None):
#     for item in os.listdir(src):
#         s = os.path.join(src, item)
#         d = os.path.join(dst, item)
#         if os.path.isdir(s):
#             shutil.copytree(s, d, symlinks, ignore)
#         else:
#             shutil.copy2(s, d)


# os.makedirs(os.path.join("build", "exe.win-amd64-3.9", "data"))

# copytree("data", os.path.join("build", "exe.win-amd64-3.9", "data"))
