"""Prints woz experiment url in GitPod"""
import hashlib
import random
import sys
import subprocess
import os
import json
import shlex
from ipython_genutils.py3compat import cast_bytes, str_to_bytes

def find_forms(data, current_key):
    result = {}
    if data is None:
        return {}
    if isinstance(data, list):
        for index, element in enumerate(data):
            result = {**result, **find_forms(element, f'{current_key}.__{element}')}
        return result
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(key, int):
                key = f'__{key}'
            if key == "!form":
                for form_key, form_value in value.items():
                    result[f'{current_key}.{key}.{form_key}'] = input(form_key)
            elif not key.startswith('!!'):
                result = {**result, **find_forms(value, f'{current_key}.{key}')}
    return result


load_instances = ""

if os.path.exists(".gitpod.woz_chat_instance.json"):
    instances_fn = ".gitpod.woz_chat_instance.json"
    with open(".gitpod.woz_chat_instance.json", "r") as f:
        data = json.load(f)
        result = find_forms(data, '')
    instances_fn += "?" + json.dumps(result)
    load_instances = f"--Newtonchat.instances={shlex.quote(instances_fn)}"

if len(sys.argv) > 1:
    # Get the password from the environment
    password_environment_variable = sys.argv[1]

    # Hash the password, this is taken from https://github.com/jupyter/notebook/blob/master/notebook/auth/security.py
    salt_len = 12
    algorithm = 'sha1'
    h = hashlib.new(algorithm)
    salt = ('%0' + str(salt_len) + 'x') % random.getrandbits(4 * salt_len)
    h.update(cast_bytes(password_environment_variable, 'utf-8') + str_to_bytes(salt, 'ascii'))
    password = ':'.join((algorithm, salt, h.hexdigest()))
else:
    password = ''

url = subprocess.check_output(['gp', 'url', '8888']).decode('utf-8').strip()
result = f"jupyter lab --NotebookApp.allow_origin='{url}' --ip='*' --NotebookApp.token='' --NotebookApp.password='{password}' --collaborative --notebook-dir experiments/woz --Newtonchat.restrict=tasks.ipynb,task1.ipynb,task2.ipynb,task3.ipynb {load_instances}"

print(result)
