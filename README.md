# SoulForgedImageStitchServer

Image Server will start a webserver that exposes 2 endpoints, one which checks if an image hash has changed, and another that accepts an image upload.

manipData will query for current paths, and create a path list with current obtained images, before creating any new image offsets.

createStitch will use the offsets generated to make a super sized version of the map of any images that can be connected to the starting node, before reducing it by a factor of 4.

To Do. 
Make the offset file usable for others to find node locations easily on the map, instead of based off the distance from the starting node.
Some sorting method to make sure older images are drawn first, and new images drawn on top, to keep the map live. 
