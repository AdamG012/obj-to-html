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
import sys
import argparse
import requests
import os
from os import chdir, getcwd
from os.path import exists, dirname, abspath

from gooey import Gooey, GooeyParser
import jinja2



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
    python obj_to_html.py tree.obj tree.html \'Tree Object\'""",
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
    parser.add_argument('output', metavar="output", type=str,  widget="FileSaver",
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


def load_raw_template(template_file, environment):
    # Load and read the template
    raw_template = None
    with open(template_file, 'r') as f:
        raw_template = f.read()

    template = environment.from_string(raw_template)
    return template


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


def obj_to_html(args, environment):
    """
    OBJ-TO-HTML Converter:
    This function will take in the arguments (mandatory being the OBJ and the outfile) and then parse the template given the files.

    Args:
    - args:     the arguments including the (max and min camera sizes, the mtl file, template files, title, object files and output name)

    """
    obj_file            = args.obj_file
    out_file            = args.output
    title               = args.title
    min_camera          = str(args.min_camera)
    max_camera          = str(args.max_camera)
    z_pos               = str(args.z_pos)
    texture_file         = args.texture
    mtl_file            = args.mtl_file
    template_file       = args.template_file

    # Load the template
    template = load_raw_template(template_file, environment)


    # Autoconvert files to canvas links if required
    if args.auto_convert:
        obj_file, texture_file, mtl_file = autoconvert_files(obj_file, texture_file, mtl_file, args.access_token, args.directory, args.prefix, args.course_number)

    # This is the context that will be sent through to the template
    template_context = {"title": title,
                "min_camera": min_camera,
                "max_camera": max_camera,
                "z_pos": z_pos}

    # If this is a OBJ + Texture
    if texture_file is not None and mtl_file is None:
        template_context.update({"texture_file": texture_url,
                             "obj_file": obj_file,
                             "load_str": """
    var manager = new THREE.LoadingManager(loadModel);
    manager.onProgress = function ( item, loaded, total ) {
        console.log( item, loaded, total );
    };
    textureLoader = new THREE.TextureLoader(manager);
    texture       = textureLoader.load('""" + texture_file + """');
    material      = new THREE.MeshPhysicalMaterial( { map : texture } );
    loader        = new OBJLoader(manager);
    loader.setCrossOrigin("");
    loader.load( '""" + obj_file + """', function ( obj ) {
        object = obj;
    }, onProgress, onError);
    """})

    # If this is a MTL File (including texture and OBJ)
    elif mtl_file is not None:
        template_context.update({"obj_file": obj_file,
                             "mtl_file": mtl_file,
                             "load_str": """
    var manager = new THREE.LoadingManager(loadModel);
    // loading MTL ontop of OBJ
    var manager   = new THREE.LoadingManager();

    manager.addHandler( /\.dds$/i, new DDSLoader() );
    // Uncomment if you need to use TGA textures
    // manager.addHandler( /\.tga$/i, new TGALoader() );

    var mtlLoader = new MTLLoader( manager )
        .load( \'""" + mtl_file + """\', function ( materials ) {
            materials.preload();
            new OBJLoader( manager )
                .setMaterials( materials )
                .load( \'""" + obj_file + """\', function ( object ) {
                    scene.add( object );
                }, onProgress, onError );
        } );
    """})

    # If this is an OBJ file conversion
    else:
        template_context['load_str'] = """var loader = new OBJLoader();
        loader.load( \'""" + obj_file + """\', function ( obj ) {
            object = obj;
            scene.add(object);
        }, onProgress, onError);
    """

    # TODO
    # If we need to load any annotations...
    annotations = False
    if annotations:
        read_js_template = "";
        load_str = """
        """

    # Create the HTML and output this
    html = template.render(template_context)
    with open(f'{out_file}', 'w') as f:
        f.write(html)

    return

if __name__ == "__main__":
    main()

