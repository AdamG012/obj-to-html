#!/usr/bin/env python3
from os import chdir, getcwd
from os.path import exists, dirname, abspath
from obj2html.utils.canvas_utils import file_to_link, autoconvert_files, convert_mtl_file


def load_raw_template(template_file, environment):
    # Load and read the template
    raw_template = None
    with open(template_file, 'r') as f:
        raw_template = f.read()

    template = environment.from_string(raw_template)
    return template


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
