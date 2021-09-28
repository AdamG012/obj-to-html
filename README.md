# OBJ To HTML Converter

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-376/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/AdamG012/obj-to-html/blob/main/LICENCE)

### Description

This small script will convert a given OBJ file to a HTML format such that it can be viewed and shared within the browser. It is a hacky solution to get around cross site scripting errors by loading your own OBJ files locally (please advise me if there is a much more sensible way to do this). The implementation involves parsing the OBJ file using ThreeJS and then adding the object to the scene. I will possibly add a method to include texture loading at a later time.

NOTE: You may have to play around with the maximum and minimum camera settings as well as Z_POS to get you image to load into view. If there is no error in the web console (press `F12` and go to the `Console` tab) then it is just an issue with the camera and position. 

### Requirements

Just good ol' python 3+ should do. However, Firefox (or possibly others) users who have tinkered with some privacy/security settings in `about:config` may run into issues if they have disabled WebGL settings. Otherwise this is working across Chromium and Firefox on the latest stable distributions.

### Acknowledgements

The code contains material and inspiration from ThreeJS : https://github.com/mrdoob/three.js/ and their examples to help load OBJ files and basically do all the heavy lifting.

### Usage and Examples

``` python
python obj_to_html.py <OBJECT_FILE> <OUTPUT_NAME> --title <TITLE> [--z_pos Z_POS] [--min_camera MIN_CAMERA] [--max_camera MAX_CAMERA]
```


Positional arguments:
  - `obj_file`: The absolute or relative path to the OBJ file.
  - `output`: The name for the output file. NOTE: Has to be suffixed by `.html`
  - `-t TITLE, --title TITLE`: The title for the HTML file.
Optional arguments:
  - `-h, --help`: Show this help message and exit
  - `--min_camera MIN_CAMERA`: The minimum distance for camera view.
  - `--max_camera MAX_CAMERA`: The maximum distance for camera view.
  - `--z_pos Z_POS`: The Z coordinate to display the camera.

Example:
                  `python obj_to_html.py tree.obj tree.html -t "Tree Object"`

### Future Work and Additions

I understand this solution will not be feasible for 1000K+ lines of object files, so I will add a method to be able to load both local `OBJ` files as well as links to `OBJ` files. Moreover, if I have time I will add some functionality for adding in textures. 

Any tips or roasts are welcome, I have 0 web dev experience so apologies for the spaghetti.
