import json, signal, sys
from wsgiref.simple_server import make_server
import dispatcher


def dispatch(environ, response):
    status = "200 OK"
    final = {}
    try:
        #dispatch request
        final = application.request(environ)
    except dispatcher.MyAppException as ex:
        status = ex.status
        final['Error'] = ex.message
        print(final)
        final_json = json.dumps(final)
    final_json = json.dumps(final)
    #return to client
    response_headers = [('Content-Type',"application/json; charset=utf-8")]
    response( status, response_headers )
    return [final_json.encode('utf-8')]

if __name__ == '__main__':
    if len(sys.argv) > 1:
        storage_type = sys.argv[1]
    else:
        storage_type = '-d'
    application = dispatcher.Dispatcher(storage_type)
    httpd = make_server( '', 8000, dispatch )
    httpd.serve_forever()
