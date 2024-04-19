import os
import hashlib
import cherrypy
import cherrypy_cors
import io
from PIL import Image

imgs = os.listdir("jpgs")

images = {}
tempHash = {}

for img in imgs:
    file = open("jpgs/" + img, "rb")
    readFile = file.read()
    sha256Hash = hashlib.sha256(readFile).hexdigest()
    #print(sha256Hash)
    images[img[:-4]] = sha256Hash
    file.close()

class myWebServer(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def hashLink(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['GET', 'POST'])
        
        if cherrypy.request.method == 'POST':
            input_json = cherrypy.request.json
            if (str(input_json["id"]) in images) and (input_json["hash"] == images[str(input_json["id"])]):
                print("Image already obtained: ID:" + str(input_json["id"]))
                return "OK"
            print("New Image Seen")
            print("ID:" + str(input_json["id"]))
            print("hash:" + input_json["hash"])
            print("myhash:" + images.get(str(input_json["id"]), "None"))
            tempHash[str(input_json["id"])] = input_json["hash"]
            return "NEED"
        
        return {'method': 'non-POST'}

    @cherrypy.expose
    def uploadLink(self, ufile):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['GET', 'POST'])
            return "OK"

        upload_path = os.path.normpath('jpgs/')
        upload_file = os.path.join(upload_path, ufile.filename)
        ba = bytearray()
        while True:
            data = ufile.file.read(8192)
            if not data:
                break
            ba.extend(data)
        sha256Hash = hashlib.sha256(ba).hexdigest()
        if tempHash[ufile.filename[:-4]] != sha256Hash:
            print("Image doesn't match sent hash, abort")
            return "Hash Mismatch"
        try:
            print(upload_file)
            image = Image.open(io.BytesIO(ba))
            print("Image Opened")
            image.crop()
            with open(upload_file, 'wb') as out:
                out.write(ba)
                images[ufile.filename[:-4]] = sha256Hash
                
                message = '''
                    length: {}
                    filename: {}
                    mime-type: {}
                    ''' .format(len(ba), ufile.filename, ufile.content_type)
                return message
        except Exception as e:
            print("Something Broke")
            print(e)
            return "Failure"
        return "Failed"

cherrypy_cors.install()
#  Setup the HTTP server that will always run
server_config={
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080,
#        'server.ssl_module':'builtin',
#        'server.ssl_certificate':'certificate.pem',
#        'server.ssl_private_key':'key.pem'
    }
cherrypy.config.update(server_config)
cherrypy.quickstart(myWebServer(), '/', {'/': {'cors.expose.on': True}})
print('Web Server is running')
