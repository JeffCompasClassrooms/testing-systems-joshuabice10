import os
import shutil
from mydb import MyDB
import pytest
import pickle
import subprocess
import time

@pytest.fixture(autouse=True)
def run_and_terminate_server():
    process = subprocess.Popen(["python3", "squirrel_server.py"])
    yield
    process.terminate()

@pytest.fixture(autouse=True)
def create_empty_database():
    if not os.path.exists("test_empty_squirrel_db.db"):
        shutil.copy("empty_squirrel_db.db", "test_empty_squirrel_db.db")
    yield
    os.remove("test_empty_squirrel_db.db")
