from PIL import Image, ImageOps, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = 368956970

StitchMap = Image.open('map.png')
new_width = int(StitchMap.size[0] * 0.4957) #could calculate dynamically, but for now just hardcode.
new_height = int(StitchMap.size[1] * 0.4948)
StitchMap = StitchMap.resize((new_width, new_height))
StitchMap.load()

ResMap = Image.open('/home/koen/sf_map/pagefile/static/map/MainMap.jpg')
ResMap.paste(StitchMap, box = (1,1011), mask = StitchMap.split()[3]) # Could calculatethe paste position, but for now just use this. Will change when exploring the north.
ResMap.save('test.jpg' , 'JPEG', quality = 80)