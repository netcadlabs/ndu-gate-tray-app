import json
import os
import tempfile
from json import JSONDecodeError

from yaml import safe_load

__temp_dir_name = os.path.join(tempfile.gettempdir(), 'ndugate')
TMP_MAX = 10000


def check_temp_folder():
    if not os.path.isdir(__temp_dir_name):
        for seq in range(TMP_MAX):
            try:
                os.mkdir(__temp_dir_name, 0o700)
                print('temporary directory created ', __temp_dir_name)
            except FileExistsError:
                continue  # try again
            except PermissionError:
                if (os.name == 'nt' and os.path.isdir(dir) and
                        os.access(dir, os.W_OK)):
                    continue
                else:
                    raise


def create_service_files(service_names):
    for service_name in service_names:
        try:
            file_name = os.path.join(__temp_dir_name, service_name + '.json')
            if os.path.isfile(file_name):
                continue
            f = open(file_name, "a")
            f.write(json.dumps({}))
            f.close()
        except Exception as e:
            print('can not create file {}'.format(file_name))
            print(e)


def get_service_setting(service_name: str, key: str):
    file_name = os.path.join(__temp_dir_name, service_name + '.json')
    if not os.path.isfile(file_name):
        return None

    settings = {}
    try:
        with open(file_name, 'r+') as f:
            settings = json.load(f)
    except JSONDecodeError as e:
        print(e)

    return settings.get(key, None)


def set_service_setting(service_name: str, key: str, value: str):
    file_name = os.path.join(__temp_dir_name, service_name + '.json')
    if not os.path.isfile(file_name):
        return None

    settings = {}
    try:
        with open(file_name, 'r+') as f:
            settings = json.load(f)
    except JSONDecodeError as e:
        print(e)

    settings[key] = value

    try:
        with open(file_name, 'w+') as f:
            f.write(json.dumps(settings))
    except JSONDecodeError as e:
        print(e)
