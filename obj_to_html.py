import sys
import argparse
from os.path import exists

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description="""
                                 OBJ To HTML Converter
                                 ---------------------
This program will convert a given OBJ file to a HTML format such that it can be viewed and shared within the browser. It is a hacky solution to get around cross site scripting errors by loading your own OBJ files locally. The implementation involves parsing the OBJ file using ThreeJS and then adding the object to the scene. I will possibly add a method to include texture loading at a later time.
The code contains material and inspiration from ThreeJS : https://github.com/mrdoob/three.js/ and their examples to help load OBJ files.

Usage:

python obj_to_html.py <OBJECT_FILE> <OUTPUT_NAME> --title <TITLE> [--z_pos Z_POS] [--min_camera MIN_CAMERA] [--max_camera MAX_CAMERA] [--texture TEXTURE_FILE]

Example:
                  python obj_to_html.py tree.obj tree.html -t "Tree Object"
         """)
parser.add_argument('obj_file', metavar="obj_file", type=str,
                    help='The absolute or relative path to the OBJ file.')
parser.add_argument('output', metavar="output", type=str,
                    help='The name for the output file. NOTE: Has to be suffixed by .html')
parser.add_argument('--min_camera', type=float, default=2,
                    help='The minimum distance for camera view.')
parser.add_argument('--max_camera', type=float, default=1000,
                    help='The maximum distance for camera view.')
parser.add_argument('--z_pos', type=float, default=250,
                    help='The Z coordinate to display the camera.')
parser.add_argument('-t', '--title', type=str, required=True,
                    help='The title for the HTML file.')
parser.add_argument('-T', '--texture', type=str, default=None,
                    help='The texture file for the object.')
args = parser.parse_args()

def obj_to_html():
    obj_file    = args.obj_file
    out_file    = args.output
    title       = args.title
    min_camera  = str(args.min_camera)
    max_camera  = str(args.max_camera)
    z_pos       = str(args.z_pos)
    texture     = args.texture

    if obj_file is None or out_file is None:
        raise ValueError("Arguments cannot be None!")

    if not exists(obj_file):
        raise ValueError("Object file path is incorrect or does not exist!")

    OUT_STR = ""
    with open(obj_file, 'r') as f:
        OUT_STR = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>""" + title + """</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
    </head>
    <body>
        <script type="module">
import * as THREE from 'https://cdn.skypack.dev/three@0.132.2/build/three.module.js';
import { OrbitControls } from 'https://cdn.skypack.dev/three@0.132.2/examples/jsm/controls/OrbitControls.js';
import { OBJLoader } from 'https://cdn.skypack.dev/three@0.132.2/examples/jsm/loaders/OBJLoader.js';

let container;
let camera, scene, renderer;
let mouseX = 0, mouseY = 0;
let windowHalfX = window.innerWidth / 2;
let windowHalfY = window.innerHeight / 2;
let object;
let objContent = `""" + f.read() + """`;
init();
animate();
function init() {
    container = document.createElement( 'div' );
    document.body.appendChild( container );
    camera = new THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight,""" + f"{min_camera}, {max_camera}); camera.position.z = {z_pos};" + """
    camera.rotation.order = 'YXZ';

    // scene
    scene = new THREE.Scene();
    const ambientLight = new THREE.AmbientLight( 0xcccccc, 0.4 );
    scene.add( ambientLight );
    const pointLight = new THREE.PointLight( 0xffffff, 0.8 );
    camera.add( pointLight );
    scene.add( camera );


    // loading object
    const loader = new OBJLoader();
    object = loader.parse(objContent);

    // loading textures
    if ( """ + ("true" if texture is not None else "false") + """ ) {
        const textureLoader = new THREE.TextureLoader();
        const texture       = textureLoader.load(""" + f"\'{texture}\'" + """);
        const material      = new THREE.MeshPhysicalMaterial( { map : texture } );
        object.traverse( function ( child ) {
            if ( child.isMesh ) child.material = material;
        });
    }

    scene.add(object);


    // Renderer setup
    renderer = new THREE.WebGLRenderer();
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    container.appendChild( renderer.domElement );

    // Orbit controls
    const orbitControls = new OrbitControls(camera, renderer.domElement);
    orbitControls.autoRotate = true;
    orbitControls.autoRotateSpeed = -2.0;
    document.body.appendChild(renderer.domElement);

    window.addEventListener( 'resize', onWindowResize );
}

function onWindowResize() {

    windowHalfX = window.innerWidth / 2;
    windowHalfY = window.innerHeight / 2;

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );

}

function animate() {

    requestAnimationFrame( animate );
    render();

}

function render() {
    camera.lookAt( scene.position );
    renderer.render( scene, camera );
}
        </script>
	</body>
</html>
"""


#        OUT_STR = HTML_STR.replace("{}", title, 1).replace("{}", f.read(), 1).replace("{}", min_camera, 1).replace("{}", max_camera, 1).replace("{}", z_pos, 1)

    with open(out_file, "w") as f:
        f.write(OUT_STR)

if __name__ == "__main__":
    obj_to_html()
