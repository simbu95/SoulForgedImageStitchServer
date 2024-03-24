import os
import hashlib
import cherrypy
import cherrypy_cors

imgs = os.listdir("jpgs")

images = {}

for img in imgs:
    file = open("jpgs/" + img, "rb")
    readFile = file.read()
    sha256Hash = hashlib.sha256(readFile).hexdigest()
    print(sha256Hash)
    images[img[:-4]] = sha256Hash
    file.close()

class myWebServer(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def SubmitNodeData(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['GET', 'POST'])
        
        if cherrypy.request.method == 'POST':
            input_json = cherrypy.request.json
            if (str(input_json["id"]) in images) and (input_json["hash"] == images[str(input_json["id"])]):
                print("Image already obtained")
                return "OK"
            print("New Image Seen")
            print("ID:" + str(input_json["id"]))
            print("hash:" + input_json["hash"])
            print("myhash:" + images.get(str(input_json["id"]), "None"))
            images[str(input_json["id"])] = input_json["hash"]
            return "NEED"
        
        return {'method': 'non-POST'}

    @cherrypy.expose
    def uploadLink(self, ufile):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['GET', 'POST'])
            return "OK"

        upload_path = os.path.normpath('jpgs/')
        upload_file = os.path.join(upload_path, ufile.filename)
        size = 0
        print(upload_file)
        with open(upload_file, 'wb') as out:
            while True:
                data = ufile.file.read(8192)
                if not data:
                    break
                out.write(data)
                size += len(data)
        out = '''
length: {}
filename: {}
mime-type: {}
''' .format(size, ufile.filename, ufile.content_type, data)
        return out


cherrypy.log.screen = None
host = '0.0.0.0'
http_port = 80
cherrypy.server.unsubscribe()
cherrypy_cors.install()
#  Setup the HTTP server that will always run
http_server = cherrypy._cpserver.Server()
http_server.socket_port = http_port
http_server._socket_host = host
http_server.subscribe()

cherrypy.tree.mount(myWebServer(), '/', {'/': {'cors.expose.on': True}})
print('Web Server is running')
if hasattr(cherrypy.engine, "console_control_handler"):
    cherrypy.engine.console_control_handler.subscribe()

#  Start / run the server
cherrypy.engine.start()
cherrypy.engine.block()