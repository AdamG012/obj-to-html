#!/usr/bin/env python3
"""
OBJ To HTML Converter:
----------------------
This program will convert a given OBJ file to a HTML format such that it can be viewed and shared within the browser. It is a hacky solution to get around cross site scripting errors by loading your own OBJ files locally. The implementation involves parsing the OBJ file using ThreeJS and then adding the object to the scene. I will possibly add a method to include texture loading at a later time.
The code contains material and inspiration from ThreeJS : https://github.com/mrdoob/three.js/ and their examples to help load OBJ files.

Usage:

python obj_to_html.py <OBJECT_FILE> <OUTPUT_NAME> <TITLE> [--z_pos Z_POS] [--min_camera MIN_CAMERA] [--max_camera MAX_CAMERA] [--texture TEXTURE_FILE] [--mtl_file MTL_FILE]

Example:
                  python obj_to_html.py tree.obj tree.html "Tree Object"

"""
from utils import *
import argparse
from gooey import Gooey, GooeyParser
import jinja2
from obj_parser import obj_to_html


@Gooey(menu=[{'name': 'Help', 'items': [{
    'type': 'AboutDialog',
    'menuTitle': 'About',
    'name': 'OBJ-to-HTML About Dialog',
    'description': """
    This program will convert a given OBJ file to a HTML format such that it can be viewed and shared within the browser.
    The implementation involves parsing the OBJ file using ThreeJS and then adding the object to the scene.
    The code contains material and inspiration from ThreeJS : https://github.com/mrdoob/three.js/ and their examples to help load OBJ files.

    Command Line Usage:
    python obj_to_html.py <OBJECT_FILE> <OUTPUT_NAME> <TITLE> [--z_pos Z_POS] [--min_camera MIN_CAMERA] [--max_camera MAX_CAMERA] [--texture TEXTURE_FILE] [--mtl_file MTL_FILE]\n\n + \

    Example:
    python obj_html_converter/obj_to_html.py tree.obj tree.html \'Tree Object\'""",
    'version': '0.2a',
    'copyright': '2022',
    'website': 'https://github.com/AdamG012/obj-to-html',
        'developer': 'https://psiduck.gitlab.io/adamg/',
    'license': 'MIT'}]}],
       program_name='OBJ To HTML Converter')
def main():
    parser = GooeyParser(description="This program will convert a given OBJ file to a HTML format such that it can be viewed and shared within the browser. " +
                         "The implementation involves parsing the OBJ file using ThreeJS and then adding the object to the scene. " + \
                         "The code contains material and inspiration from ThreeJS : https://github.com/mrdoob/three.js/ and their examples to help load OBJ files.\n\nUsage:\n" + \
                         "python obj_to_html.py <OBJECT_FILE> <OUTPUT_NAME> <TITLE> [--z_pos Z_POS] [--min_camera MIN_CAMERA] [--max_camera MAX_CAMERA] [--texture TEXTURE_FILE] [--mtl_file MTL_FILE]\n\n" + \
                         "Example:\npython obj_to_html.py tree.obj tree.html -t \'Tree Object\'\n")


    # Required Arguments
    parser.add_argument('obj_file', metavar="obj_file", type=str, widget="FileChooser",
                        help='The absolute or relative path to the OBJ file.')
    parser.add_argument('output', metavar="output", type=str, default="out/", widget="FileSaver",
                        help='The name for the output file. NOTE: Has to be suffixed by .html')
    parser.add_argument('title', type=str,
                        help='The title for the HTML file.')

    # Optional View Settings
    view_options_group = parser.add_argument_group(
        "View Options [OPTIONAL]",
        "Optional view settings which should be configured to correctly display the OBJ file.")
    view_options_group.add_argument('--min_camera', type=float, default=2, widget="DecimalField", gooey_options={'min': 0, 'max': 10000},
                        help='The minimum distance for camera view.')
    view_options_group.add_argument('--max_camera', type=float, default=1000, widget="DecimalField", gooey_options={'min': 0, 'max': 100000},
                        help='The maximum distance for camera view.')
    view_options_group.add_argument('-z', '--z_pos', type=float, default=250, widget="DecimalField", gooey_options={'min': 0, 'max': 100000},
                        help='The Z coordinate to display the camera.')
    view_options_group.add_argument('--template_file', type=str, default="./templates/default.html", widget="FileChooser",
                        help='The template file for the HTML.')

    # Texture, Material and Other 3D Settings
    three_dim_settings_group = parser.add_argument_group(
        "3D Options [OPTIONAL]",
        "3D Settings and parameters including whether to use texture or material files.")
    three_dim_settings_group.add_argument('-T', '--texture', type=str, default=None, widget="FileChooser",
                        help='The texture file for the object.')
    three_dim_settings_group.add_argument('-m', '--mtl_file', type=str, default=None, widget="FileChooser",
                                          help='The texture file for the object. NOTE: You must provide the relative (to the file)/absolute paths of the texture files within the mtl file.')

    # Auto Conversion Settings
    auto_convert_group = parser.add_argument_group(
        "Canvas auto-convert [OPTIONAL]",
        "Provide the ability to auto-convert and upload links to Canvas for use in pages.")
    auto_convert_group.add_argument('--auto_convert', action='store_true',
                        help='Whether to auto convert the links to Canvas files.')
    auto_convert_group.add_argument('--save_token', action='store_true',
                        help='Whether to save the token for later use.')
    auto_convert_group.add_argument('--access_token', metavar="access_token", widget="PasswordField",
                        type=str, default=None, help='The access token generated in canvas settings. LEAVE EMPTY TO LOAD TOKEN FROM SAVED DIRECTORY.')
    auto_convert_group.add_argument('--directory', metavar="directory",
                        type=str, default="", help='The directory to upload to on Canvas.')
    auto_convert_group.add_argument('--course_number', metavar="c", type=int,
                                    help='OPTIONAL: The course number of the canvas link.', default=None)
    auto_convert_group.add_argument('-p', '--prefix', type=str,
                        help='The canvas infrastructure to use e.g. canvas.sydney.edu.au', default="canvas.sydney.edu.au")

    args = parser.parse_args()

    # If we want to load from saved file
    if args.auto_convert and args.access_token is None:
        args.access_token = load_token(args.prefix)

    # If we want to save this token
    if args.auto_convert and args.access_token is not None and args.save_token:
        save_token(args.access_token, args.prefix)


    # Render Jinja2 environment
    environment = jinja2.Environment()
    obj_to_html(args, environment)


if __name__ == "__main__":
    main()

