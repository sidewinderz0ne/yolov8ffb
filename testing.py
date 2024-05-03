import subprocess
import time
import os
import json
from pathlib import Path
import argparse
from urllib.request import urlopen

import requests

url = "https://srs-ssms.com/grading_ai/get_list_mill.php"

try:
    response = requests.get(url)
    arr = response.json()
    
except Exception as e:
    print("Error fetching data from the server:", e)
