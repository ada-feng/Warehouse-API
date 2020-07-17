import json, signal, sys, re
import urllib.parse
import storage, storage_file, storage_db



httpMethods=["GET", "POST",'PUT','DELETE']
expected_request_ctype = "application/json; charset=utf-8"

class MyAppException( Exception):
    status = ''
    message = ''
    def __init__(self, statusORcopy, message =None):
        if message == None:
            self.status = statusORcopy.status
            self.message = statusORcopy.message
        else:
            self.status = statusORcopy
            self.message = message

class Dispatcher(object):
    def __init__(self, argument):
        self.resources = [{"pathway": "/parts", "object":Parts(argument)}]
        self.resources.append({"pathway": "/orders", "object":Orders()})

    @staticmethod
    def environChecker(environ):
        request_method = environ['REQUEST_METHOD'].upper()

        if request_method not in httpMethods:
            raise MyAppException("400 Bad Request","Unknown HTTP method")

        length = 0
        if 'CONTENT_LENGTH' in environ and environ['CONTENT_LENGTH']!="":
            length = int( environ['CONTENT_LENGTH'])
        if length < 0:
            raise MyAppException("400 Bad Request","Illegal CONTENT_LENGTH")

        if environ['CONTENT_TYPE'] != expected_request_ctype:
            raise MyAppException("400 Bad Request","Unexpected content type: "\
            +environ['CONTENT_TYPE'] +", expects "+ expected_request_ctype )
        return request_method, length

    def request(self, environ):
        path = environ['PATH_INFO']
        request_method, length = self.environChecker( environ)
        if length == 0:
            body_dic = None
        else:
            body_encoded = environ['wsgi.input'].read(length)
            try:
                body_json = body_encoded.decode('utf-8')
                body_dic = json.loads(body_json)
            except:
                raise MyAppException("400 Bad Request","Unexpected content type")

        for rscs in self.resources:
            if path == rscs['pathway']:
                return rscs['object'].request( request_method, body_dic)
        raise MyAppException('404 Not Found','Invalid pathway')

class Parts(object):

    def __init__(self, argument):
        if (argument=="-d"):
            print ("Using Data Base")
            self.myInventory = storage_db.storage_db()
        elif (argument == "-f"):
            self.myInventory = storage_file.storage_file()
        else:
            self.myInventory = storage_file.storage_file()

    def handleGET(self, body_dic):
        result = {}
        if body_dic == None:
            result = self.myInventory.getAll()

        elif 'name' in body_dic:
            key = body_dic['name']
            try:
                value = self.myInventory.get(key)
            except OEx as ex:
                raise MyAppException(ex)
            result[key] = value

        elif ('upper bound' in body_dic ) or ('lower bound' in body_dic):
            upperBound_str = None
            lowerBound_str = None
            if 'upper bound' in body_dic:
                upperBound_str = body_dic['upper bound']
            if 'lower bound' in body_dic:
                lowerBound_str = body_dic['lower bound']
            try:
                result = self.myInventory.boundSearch(upperBound_str, lowerBound_str)
            except OEx as ex:
                raise MyAppException(ex)

        else: #body is not None, yet no useful parameters
            raise MyAppException("400 Bad Request, Meaningless body")
        #if nothing goes wrong
        return result

    #returns a dictionary
    def request( self, request_method, body_dic):
        result={}
        if request_method == 'GET':
            result = self.handleGET(body_dic)

        elif request_method == 'PUT' or request_method == 'POST':
            if body_dic == None:
                raise MyAppException("400 Bad Request", "This method require a body")
            try:
                result = self.myInventory.update(body_dic)
            except storage.InventoryException as ex:
                raise MyAppException(ex)
            finally:
                self.myInventory.save()

        #if request_method == 'DELETE'
        else:
            if body_dic == None:
                raise MyAppException("400 Bad Request", "This method require a body")
            try:
                key = body_dic['name']
            except:
                raise MyAppException("400 Bad Request", "Need to include\
                 { 'name' = 'item name' } in the request body")
            try:
                self.myInventory.remove(key)
            except storage.InventoryException as ex:
                raise MyAppException(ex)
            finally:
                self.myInventory.save()
        return result

