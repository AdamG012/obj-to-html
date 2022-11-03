#!/usr/bin/env python3
import os
import requests


def get_config_dir():
    home_path = os.path.expanduser('~')
    if os.name == 'nt':
        home_path += f'/Documents/obj_to_html/'
    elif os.name == 'posix':
        home_path += f'/.config/obj_to_html/'

    return home_path


def grab_canvas_urls(file_name, access_token, course_num, prefix):
    if file is None or len(files) == 0:
        raise ValueError("Invalid configuration, no files entered.")

    request = requests.get("https://{}/api/v1/{}files/{}?access_token={}".format(prefix, course_num, file_name, access_token))
    if request is None or 'url' not in request.json():
            raise ValueError(f"Invalid configuration for {f}, check your arguments.\nGenerated request:\n{request}")

    url    = request.json()['url']
    return url


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

    # TODO Warning this will overwrite existing files uploaded
    file_name=os.path.basename(file_path)

    if course_num == None:
        course_num = "users/self/"

    # Step 1: Notify Canvas of the file upload
    params = {"parent_folder_path": directory,
              "name": file_name}
    authorisation = {'Authorization': f'Bearer {access_token}'}
    initial_req = requests.post(f"https://{prefix}/api/v1/{course_num}files/", params=params, headers=authorisation)

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


def upload_file(file_name, access_token, course_num, prefix):
    pass


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
