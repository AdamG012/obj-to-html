#!/usr/bin/env python3
import os
from os.path import exists, dirname, abspath
import requests


def get_config_dir():
    home_path = os.path.expanduser('~')
    if os.name == 'nt':
        home_path += f'/Documents/obj_to_html/'
    elif os.name == 'posix':
        home_path += f'/.config/obj_to_html/'

    return home_path


def convert_mtl_file(mtl_file, access_token, directory, prefix=None, course_num=None):
    # Change the current path to be relative to the MTL file
    # This is done so that users don't have to go into the file and
    # modify the paths to be relative to the working direcotry
    curr_path = abspath(getcwd())
    chdir(dirname(abspath(mtl_file)))

    # Update the MTL file with the link of the texture file
    mtl_raw = None
    with open(mtl_file, 'r') as f:
        mtl_raw = f.readlines()

    # Find the unique lines mapping to the texture files
    map_kds = {}

    # Loop over finding lines that match the texture files
    for i, line in enumerate(mtl_raw):
        if "map_Kd" in line:
            text_url = None
            line = line.strip()

            # If not in the map then autoconvert the link
            if line not in map_kds:
                texture_path = line.split(" ")[1]
                text_url = file_to_link(file_path=texture_path, access_token=access_token,
                        directory=directory, prefix=prefix, course_num=course_num)
                map_kds[line] = text_url

            # If we have converted this link before
            else:
                text_url = map_kds[line]
            mtl_raw[i] = f"map_Kd {text_url}\n"

    # To not overwrite the existing file
    mtl_file = mtl_file[:-4] + "_online.mtl"
    with open(mtl_file, 'w') as f:
        f.write("".join(mtl_raw))

    # Change the directory back to the working DIR
    chdir(abspath(curr_path))

    # Convert MTL File
    return file_to_link(file_path=mtl_file, access_token=access_token, directory=directory, prefix=prefix, course_num=course_num)


def autoconvert_files(obj_file, texture_file, mtl_file, access_token, directory, prefix=None, course_num=None):
    # Convert OBJ
    obj_url = file_to_link(file_path=obj_file, access_token=access_token,
                           directory=directory, prefix=prefix, course_num=course_num)
    texture_url = None
    mtl_url = None

    # Convert Texture File
    if mtl_file is None and texture_file is not None:
        texture_url = file_to_link(file_path=texture_file, access_token=access_token,
                                   directory=directory, prefix=prefix, course_num=course_num)

    # Convert the MTL File
    if mtl_file is not None:
        mtl_url = convert_mtl_file(mtl_file, access_token, directory, prefix, course_num)

    return obj_url, texture_url, mtl_url


def file_to_link(file_path, access_token, directory, prefix, course_num=None):
    """
    Given the file name it will upload it to the Canvas site and directory indicated.

    Args:
    - file_name         : path of the file to be uploaded
    - access_token      : access token for uploading to Canvas
    - directory         : the directory to upload to
    - prefix            : the Canvas host to use
    - course_num        : the course number if uploading to a specific course
    """

    # NOTE Warning this will overwrite existing files uploaded
    file_name=os.path.basename(file_path)

    # Set the course path to the users files or to a course's files
    course_path = ""
    if course_num == None:
        course_path = "users/self/"
    else:
        course_path = f"courses/{course_num}/"

    # Step 1: Notify Canvas of the file upload
    params = {"parent_folder_path": directory,
              "name": file_name}
    authorisation = {'Authorization': f'Bearer {access_token}'}

    initial_req = requests.post(f"https://{prefix}/api/v1/{course_path}files/", params=params, headers=authorisation)

    # Get the JSON
    request_json = initial_req.json()

    file_upload = request_json['upload_params']['file'] if 'file' in request_json else file_path

    # Step 2: Upload the actual data to Canvas
    upload_req = requests.post(f"{request_json['upload_url']}", params=request_json['upload_params']['filename'], files={"file": open(file_upload, 'rb')})

    # Get the JSON
    upload_json = upload_req.json()

    # Step 3: Confirm that the upload was successful if we are given a location
    if 'location' in upload_json:
        confirm_req = requests.post(f"{upload_json['location']}", headers=authorisation, params=params)

    return upload_json['url']


def save_token(access_token, prefix):

    # Check if invalid
    if prefix is None:
        raise ValueError("Prefix cannot be none!")

    prefix_file = prefix.replace(".", "_")
    home_path = get_config_dir() + "/tokens"

    # if the directory does not exist
    if not os.path.exists(home_path):
        os.makedirs(home_path)

    home_path += f"{prefix_file}_access_token"

    with open(home_path, 'w') as f:
        f.write(access_token)


def load_token(prefix):

    # Check if invalid
    if prefix is None:
        raise ValueError("Prefix cannot be none!")

    prefix_file = prefix.replace(".", "_")
    home_path = get_config_dir() + "/tokens"

    # if the directory does not exist
    if not os.path.exists(home_path):
        raise ValueError("The access token does not exist!")

    home_path += f"{prefix_file}_access_token"

    access_token = None
    with open(home_path, 'r') as f:
        access_token = f.read().strip()

    return access_token
