import os
import sys
from pathlib import Path
# DATA_DIR = Path(os.getcwd()).parents[0] 
DATA_DIR = Path(os.path.abspath(sys.argv[0])).parents[1] 
# MAIN_DIR = Path(__file__).parents[0]
SCHEDULE_PATH = os.path.join(Path(os.path.abspath(sys.argv[0])).parents[1], 'scheduling', 'dist', 'main.exe') 
print(DATA_DIR)