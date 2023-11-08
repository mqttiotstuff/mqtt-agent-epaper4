#!/bin/python3

import json
import traceback

import xml.dom.minidom
import xml.dom


def findSubById(node, searchid):
    """
        find a node having the given searchid
    """
    assert searchid is not None
    if node is None:
        return None

    if isinstance(node,xml.dom.minidom.Element):
        a = node.getAttribute("id")
        if a is not None and a == searchid:
            return node

    for i in node.childNodes:
       ret = findSubById(i, searchid)
       if ret is not None:
           return ret
    return None

def replaceText(node, dom, replace):
    assert node is not None
    assert dom is not None
    assert replace is not None

    textNode = dom.createTextNode(replace)
    while len(node.childNodes) > 0:
        node.removeChild(node.childNodes[0])
    node.appendChild(textNode)

def construct_image(svgfile, replaced_text):

    dom = xml.dom.minidom.parse("Meteo.svg")
    for k in replaced_text:
        e = findSubById(dom, k)
        print(e)
        replaceText(e.childNodes[0], dom, replaced_text[k])

    print(dom.toprettyxml())
    dom.writexml(open("result.svg", "w"))
    import cairosvg
    cairosvg.svg2png(url="result.svg", write_to="output.png", output_width=400, output_height=300)

    from PIL import Image
    image = Image.open("output.png")

    tilex = 4 * 2
    tiley = 3 * 2

    result = []
    for i in range(0,tilex):
        stepx = 400 // tilex;
        stepy = 300 // tiley;
        for j in range(0,tiley):
            bounds = (i*stepx, j*stepy, (i+1)*stepx, (j+1)*stepy) 
            crop_image = image.crop(bounds)
            newformat = crop_image.convert("1")
            b = newformat.tobytes()
            element = (bounds[0],bounds[1], stepx, stepy, b)
            result.append(element)

    return result



