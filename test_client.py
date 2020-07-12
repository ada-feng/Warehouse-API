import http.client, pprint, sys, json
import unittest

class inventory_client():
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

class TestAPIResponse(unittest.TestCase):
    path = '/parts'
    def setUp(self):
        self.iv_client = inventory_client()

    def TestGenericExceptions(self):
        ok_method = 'GET'
        ok_path = '/parts'
        wrong_method = 'GEET'
        with self.assertRaises(Exception):
            self.iv_client.httpmethod(wrong_method, ok_path)

        wrong_path = "/inventory"
        with self.assertRaises(Exception):
            self.iv_client.httpmethod(ok_method, wrong_path)

        wrong_content_type_headers = {'Content-type':'text/plain'}
        with self.assertRaises(Exception):
            self.iv_client.httpmethod(ok_method, ok_path, None, \
            wrong_content_type_headers)

        wrong_content_length_headers = {'Content-length': -5}
        with self.assertRaises(Exception):
            self.iv_client.httpmethod(ok_method, ok_path, None, \
            wrong_content_length_headers)

        wrong_body_encoding = ( json.dumps({'name': 'a'}) ).encode('utf-16')
        with self.assertRaises(Exception):
            self.iv_client.httpmethod(ok_method, ok_path, wrong_body_encoding)

        wrong_body_format = ("{'name': 'a'}" ).encode('utf-8')
        with self.assertRaises(Exception):
            self.iv_client.httpmethod(ok_method, ok_path, wrong_body_format)

    def testGetAll(self):
        body_dic = None
        status, response_body = self.iv_client.httpmethod('get', self.path, body_dic)
        self.assertEqual(status, 200 )
        self.assertIsNotNone(response_body)
        self.assertTrue(isinstance(response_body, dict) )

    def testGetExistItem(self):
        setup_dic = {"a": "6"}
        setup_dic_formatted = self.iv_client.response_body_formatter(setup_dic)
        self.iv_client.httpmethod("PUT", self.path, setup_dic_formatted)
        request_body_dic = {'name': 'a'}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        status, response_body  =  self.iv_client.httpmethod('get', self.path, \
        request_body_formatted)
        self.assertEqual(status, 200 )
        self.assertTrue( response_body == {'a':6})

    # this method also ckecks that put one item with quantity and
    #delete an existing item function correctly
    def testGetNotExistItem(self):
        #first put 'a' in the inventory
        setup_dic = {"a": "6"}
        setup_dic_formatted = self.iv_client.response_body_formatter(setup_dic)
        status, response_body = self.iv_client.httpmethod("PUT", self.path, setup_dic_formatted)
        self.assertEqual(status, 200 )
        self.assertTrue( response_body == {'a':6})
        #now delete "a", so it cannot be in the inventory
        request_body_dic = {'name': 'a'}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        status, response_body = self.iv_client.httpmethod('DELETE', self.path,request_body_formatted)
        self.assertEqual(status, 200 )
        self.assertEqual( response_body, {})
        #now query th string
        request_body_dic = {"name": "a"}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        with self.assertRaises(Exception):
            self.iv_client.httpmethod('get', self.path, request_body_formatted)

    def testGetOnlyUpperBound(self):
        setup_dic = {"a": "25", "b":6, "c":"26"}
        setup_dic_formatted = self.iv_client.response_body_formatter(setup_dic)
        self.iv_client.httpmethod("PUT", self.path, setup_dic_formatted)
        request_body_dic = {'upper bound': '25'}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        status, response_body  =  self.iv_client.httpmethod('get', self.path, \
        request_body_formatted)
        self.assertEqual(status, 200 )
        self.assertTrue(response_body["a"] ==25)
        self.assertTrue(response_body["b"] ==6)
        self.assertTrue("c" not in response_body)

    def testGetOnlyLowerBound(self):
        setup_dic = {"a": "25", "b":6, "c":"7"}
        setup_dic_formatted = self.iv_client.response_body_formatter(setup_dic)
        self.iv_client.httpmethod("PUT", self.path, setup_dic_formatted)
        request_body_dic = {'lower bound': '7'}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        status, response_body  =  self.iv_client.httpmethod('get', self.path,\
         request_body_formatted)
        self.assertEqual(status, 200 )
        self.assertTrue(response_body["a"] ==25)
        self.assertTrue("b" not in response_body)
        self.assertTrue(response_body["c"] ==7)

    def testGetBothBounds(self):
        setup_dic = {"a": "17", "b":16, "c":"300", 'd':301}
        setup_dic_formatted = self.iv_client.response_body_formatter(setup_dic)
        self.iv_client.httpmethod("PUT", self.path, setup_dic_formatted)
        request_body_dic = {'lower bound': '17', 'upper bound': 300}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        status, response_body  =  self.iv_client.httpmethod('get', self.path, \
        request_body_formatted)
        self.assertEqual(status, 200 )
        self.assertTrue(response_body["a"] ==17)
        self.assertTrue("b" not in response_body)
        self.assertTrue(response_body["c"] ==300)
        self.assertTrue("d" not in response_body)

    def testGetIllegalBounds(self):
        lowerHigherThanUpper_dic = {'lower bound': '17', 'upper bound': 3}
        lowerHigherThanUpper_dic_formatted \
        = self.iv_client.response_body_formatter(lowerHigherThanUpper_dic)
        status, response_body  =  self.iv_client.httpmethod('get', self.path, \
        lowerHigherThanUpper_dic_formatted)
        self.assertEqual(status, 200 )
        self.assertEqual(response_body, {} )

        notInteger_dic = {'lower bound': '1.7', 'upper bound': "hello"}
        notInteger_dic_formatted \
        = self.iv_client.response_body_formatter(notInteger_dic)
        with self.assertRaises(Exception):
            self.iv_client.httpmethod('get', self.path, notInteger_dic_formatted)

    def testPutNormal(self):
        #a normal dictionary with names of integer/strings of integer values
        request_body_dic = {"a": 5, "b": "6", "c":85}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        status, response_body = self.iv_client.httpmethod("PUT", self.path, request_body_formatted)
        self.assertEqual(status, 200 )
        self.assertEqual(response_body, {"a": 5, "b": 6, "c":85} )

    def testPutNegative(self):
        #a normal dictionary with names of integer/strings of integer values
        request_body_dic = {"a": 5, "b": -6}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        with self.assertRaises(Exception):
            self.iv_client.httpmethod("PUT", self.path, request_body_formatted)

    def testPutIncDec(self):
        #set up
        request_body_dic = {"a": 5, "b": "6", "c":85}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        self.iv_client.httpmethod("PUT", self.path, request_body_formatted)
        #increase or decrease
        request_body_dic = {"a": "-3", "b": "+2", "c": +60}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        status, response_body = self.iv_client.httpmethod("PUT", self.path, request_body_formatted)
        self.assertEqual(status, 200 )
        self.assertEqual(response_body, {"a": 2, "b": 8, "c":+60} )

    def testPutIncDecResultNegative(self):
        #set up
        request_body_dic = {"a": 5, "b": "6"}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        self.iv_client.httpmethod("PUT", self.path, request_body_formatted)

        #increase or decrease
        request_body_dic = {"a": "-7", "b": "+2"}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        with self.assertRaises(Exception):
            self.iv_client.httpmethod("PUT", self.path, request_body_formatted)


    def testPutWeirdStringAndAtomic(self):
        #set up
        request_body_dic = {"a": "7", "b": "2"}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        self.iv_client.httpmethod("PUT", self.path, request_body_formatted)

        #increase or decrease
        request_body_dic = {"a": "6.05", "b": "6"}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        with self.assertRaises(Exception):
            self.iv_client.httpmethod("PUT", self.path, request_body_formatted)

        #test if b is changed
        request_body_dic = {"name": "b"}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        status, response_body = self.iv_client.httpmethod("get", self.path, request_body_formatted)
        self.assertEqual(response_body["b"], 2)

    #regular delete is tested by testGetNotExistItem
    def testDeleteNonExist(self):
        #set up
        request_body_dic = {"a": "2"}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        self.iv_client.httpmethod("PUT", self.path, request_body_formatted)

        #delete the item a
        request_body_dic = {"name": "a"}
        request_body_formatted = self.iv_client.response_body_formatter(request_body_dic)
        self.iv_client.httpmethod("DELETE", self.path, request_body_formatted)

        #now we shouldn't be able to do it again
        request_body_dic = {"name": "b"}
        with self.assertRaises(Exception):
            self.iv_client.httpmethod("DELETE", self.path, request_body_formatted)


if __name__ == '__main__':
    unittest.main()
