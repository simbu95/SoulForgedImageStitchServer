import json
import os
from Stitch import resizeImage
from PIL import Image, ImageOps
fileList = os.listdir('jpgs/')
startFile = "3878924"
#startFile = "3880088"
Bounds = {"minx" : 0, "miny": 0, "maxx": 0, "maxy": 0}

def NodeWalk(Offsets, Bounds, Adj, currentNode):
    currentOffset = Offsets[currentNode]
    if Bounds["minx"] > currentOffset[0]:
        Bounds["minx"] = currentOffset[0]
    if Bounds["maxx"] < currentOffset[0]:
        Bounds["maxx"] = currentOffset[0]
    if Bounds["miny"] > currentOffset[1]:
        Bounds["miny"] = currentOffset[1]
    if Bounds["maxy"] < currentOffset[1]:
        Bounds["maxy"] = currentOffset[1]
    for node in Adj[currentNode].keys():
        if (not node in Offsets) and ('offset' in Adj[currentNode][node]):
            nodeOffset = Adj[node][currentNode]['offset'] #This might need to be swapped.
            Offsets[node] = ( currentOffset[0] + nodeOffset[0] , currentOffset[1] + nodeOffset[1] )
            NodeWalk(Offsets, Bounds, Adj, node)
 
with open("sample.json", "r") as mapFile:
    Adj = json.load(mapFile)
    Offsets = {}
    Offsets[startFile] = (0,0)
    NodeWalk(Offsets, Bounds, Adj, startFile)
    
    new_width = Bounds["maxx"] - Bounds["minx"] + 4000
    new_height = Bounds["maxy"] - Bounds["miny"] + 4000
    
    mask = Image.open('Mask.png').convert('L')
    Canvas = Image.new('RGBA', (new_width, new_height), (0,0,0,0))
    for file in fileList:
        node, ext = os.path.splitext(file)
        if node in Offsets:
            addIM = Image.open('jpgs/' + file)
            addIM = resizeImage(addIM)
            addMask = ImageOps.fit(mask, addIM.size, centering=(0.5, 0.5))
            addIM.putalpha(addMask.convert('1'))
            
            diffx = Offsets[node][0] - Bounds["minx"]
            diffy = Offsets[node][1] - Bounds["miny"]
            
            Canvas.paste(addIM, (diffx, diffy), addIM)
    
    Canvas = Canvas.reduce(4)
    imageBox = Canvas.getbbox()
    cropped = Canvas.crop(imageBox)
    cropped.save('map.png')
    cropped.show()
   
    json_object = json.dumps(Offsets, indent=2)
    with open("offsets.json", "w") as outfile:
        outfile.write(json_object)