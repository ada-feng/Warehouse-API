import http.client, pprint, sys, json
import unittest

class order_client():
    expected_ctype = "application/json; charset=utf-8"
    http_methods=["GET", "POST",'PUT','DELETE']
    get_options =['get all','query with bounds','find a specific item']

    def __init__(self):
        self.connection = http.client.HTTPConnection('localhost:8000')

    def httpmethod(self, method, path, body = None,\
                    headers= {'Content-type':"application/json; charset=utf-8"} ):

        self.connection.request(method, path, body, headers)
        response = self.connection.getresponse()
        ctype = response.getheader('Content-type')
        status_code =  response.status
        print (status_code)
        if status_code>= 500:
            raise Exception("HTTP call failed: "+ str(status_code )+" "+ response.reason)
        if ctype != self.expected_ctype:
            raise Exception("Unexpected response content type "+ ctype)
        body_dic = json.loads( response.read().decode('utf-8') )
        if status_code != 200:
            print (body_dic)
            raise Exception("HTTP call failed: "+ str(status_code )+" "\
            + response.reason + ", " + body_dic['Error'])
        print(body_dic)
        return status_code, body_dic

    @staticmethod
    def response_body_formatter(body_dic):
        return (json.dumps(body_dic)).encode('utf-8')

class TestAPIOrdersResponse(unittest.TestCase):
    path = '/orders'
    def setUp(self):
        self.order_client = order_client()

    def TestGenericExceptions(self):
        ok_method = 'GET'
        ok_path = '/orders'
        wrong_method = 'GEET'
        with self.assertRaises(Exception):
            self.order_client.httpmethod(wrong_method, ok_path)

        wrong_path = "/inventory"
        with self.assertRaises(Exception):
            self.order_client.httpmethod(ok_method, wrong_path)

        wrong_content_type_headers = {'Content-type':'text/plain'}
        with self.assertRaises(Exception):
            self.order_client.httpmethod(ok_method, ok_path, None, \
            wrong_content_type_headers)

        wrong_content_length_headers = {'Content-length': -5}
        with self.assertRaises(Exception):
            self.order_client.httpmethod(ok_method, ok_path, None, \
            wrong_content_length_headers)

        wrong_body_encoding = ( json.dumps({'name': 'a'}) ).encode('utf-16')
        with self.assertRaises(Exception):
            self.order_client.httpmethod(ok_method, ok_path, wrong_body_encoding)

        wrong_body_format = ("{'name': 'a'}" ).encode('utf-8')
        with self.assertRaises(Exception):
            self.order_client.httpmethod(ok_method, ok_path, wrong_body_format)

    def testGetAll(self):
        body_dic = None
        status, response_body = self.order_client.httpmethod('get', self.path, body_dic)
        self.assertEqual(status, 200 )
        self.assertIsNotNone(response_body)
        self.assertTrue(isinstance(response_body, dict) )

    def testGetOrderBasedOnUser(self):
        setup_dic = {"user name":"clever user", "date":"05/20/2017","total": 27.5}
        setup_dic_formatted = self.order_client.response_body_formatter(setup_dic)
        status, response_body = self.order_client.httpmethod("POST", self.path, setup_dic_formatted)
        self.assertEqual(status, 200 )
        request_body_dic = {"user name":"clever user"}
        request_body_formatted = self.order_client.response_body_formatter(request_body_dic)
        status, response_body  =  self.order_client.httpmethod('get', self.path, \
        request_body_formatted)
        self.assertEqual(status, 200 )
        self.assertTrue( response_body ['05/20/2017']:27.5)

    def testPostPutCorrect(self):
        setup_dic = {"user name":"clever user", "date":"05/20/2017","total": 27.5}
        setup_dic_formatted = self.order_client.response_body_formatter(setup_dic)
        status, response_body = self.order_client.httpmethod("POST", self.path, setup_dic_formatted)
        self.assertEqual(status, 200)

        find_dic = setup_dic
        replace_dic = {"user name":"changed it", "date":"05/20/1799","total": "35.8"}
        request_body_dic ={'find':setup_dic, 'replace': replace_dic}
        request_body_formatted = self.order_client.response_body_formatter(request_body_dic)
        status, response_body = self.order_client.httpmethod("Put", self.path, request_body_formatted)
        self.assertEqual(status, 200)


    def testPOSTWrong(self):
        setup_dic = {"user name":"clever user", "date":"05/20/2017"}
        setup_dic_formatted = self.order_client.response_body_formatter(setup_dic)
        with self.assertRaises(Exception):
            self.order_client.httpmethod("POST", self.path, setup_dic_formatted)



if __name__ == '__main__':
    unittest.main()
