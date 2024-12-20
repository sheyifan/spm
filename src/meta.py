import os.path
from os.path import dirname, realpath
import sys

executable_dir = dirname(dirname(realpath(__file__)))
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    executable_dir = dirname(getattr(sys, "_MEIPASS"))

default_projects_url = os.path.join(executable_dir, "projects")
mete_file = os.path.join(default_projects_url, "metadata.db")
