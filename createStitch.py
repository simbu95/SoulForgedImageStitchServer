import json
import os
from Stitch import resizeImage
from PIL import Image, ImageOps, ImageDraw
search_dir = "jpgs/"
fileList = os.listdir('jpgs/')
fileList.sort(key=lambda x: os.path.getmtime('jpgs/' + x))
#startFile = "3878924"
startFile = "9271"
#startFile = "23377"
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
    centers = {}
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
            center = addIM.size[0]/2
            centers[node] = ((diffx + center)/4, (diffy + center)/4)
    Canvas = Canvas.reduce(4)
    imageBox = Canvas.getbbox()
    cropped = Canvas.crop(imageBox)
    cropped.save('map.png')
    draw = ImageDraw.Draw(cropped)
    for cen in centers.keys():
        draw.ellipse((centers[cen][0]-15,centers[cen][1]-15,centers[cen][0]+15,centers[cen][1]+15), fill = 'red')
    png = cropped.reduce(4)
    png.load() # required for png.split()
    background = Image.new("RGB", png.size, (255, 255, 255))
    background.paste(png, mask=png.split()[3])
    background.save('dots.jpg', quality=90)
   
    json_object = json.dumps(centers, indent=2)
    with open("centers.json", "w") as outfile:
        outfile.write(json_object)