import requests
import json
import os
from Stitch import ImageOffset

Adjacent = {}
print("start")
with open("sample.json", "r") as mapFile:
    Adjacent = json.load(mapFile)


print("file Open")
with requests.Session() as s:
    p = s.post("https://soul-forged-resourcs-map.vercel.app/getDataSet", data={"item": "mapRouteMain"})
    MapPaths = json.loads(p.text.replace("\'", "\""))
    print("Path Dataset")
    
    p = s.post("https://soul-forged-resourcs-map.vercel.app/getDataSet", data={"item": "nodeMaping"})
    nodeMapping = json.loads(p.text.replace("\'", "\""))
    nodeMap = dict((v,k) for k,v in nodeMapping.items())
    print("Node Dataset")
    
    for path in MapPaths:
        if path['start'] in nodeMap and path['end'] in nodeMap:
            if not nodeMap[path['start']] in Adjacent:
                Adjacent[nodeMap[path['start']]] = {}
            
            if not nodeMap[path['end']] in Adjacent:
                Adjacent[nodeMap[path['end']]] = {}
            
            if not nodeMap[path['end']] in Adjacent[nodeMap[path['start']]]:
                Adjacent[nodeMap[path['start']]][nodeMap[path['end']]] = {}
            
            if not nodeMap[path['start']] in Adjacent[nodeMap[path['end']]]:
                Adjacent[nodeMap[path['end']]][nodeMap[path['start']]] = {}

print("Image Start")
myjpgs = os.listdir('jpgs/')
nodeList = []
for file in myjpgs:
    module_name, ext = os.path.splitext(file)
    nodeList.append(module_name)
for node in Adjacent.keys():
    if node in nodeList:
        for dest in Adjacent[node]:
            if not "offset" in Adjacent[node][dest] and dest in nodeList:
                (success, offset) = ImageOffset(node + ".jpg", dest + ".jpg")
                if success:
                    print(node + " is connected to " + dest + " with an offset of\n\tRight:" + str(offset[0]) + " \n\tDown:" + str(offset[1]))
                    Adjacent[node][dest]["offset"] = offset
                    Adjacent[dest][node]["offset"] = (-offset[0],-offset[1])
                else:
                    print("Error, couldn't find a match, investigate:" + node + "," + dest)
missing = set(nodeMapping.keys()) - set(nodeList)
missList = []
for miss in missing:
    missList.append(nodeMapping[miss])
missList.sort()
json_object = json.dumps(Adjacent, indent=2)
with open("sample.json", "w") as outfile:
    outfile.write(json_object)

miss_object = json.dumps(missList, indent=2)
with open("misses.json", "w") as outfile:
    outfile.write(miss_object)