from storage import InventoryException, storage
import json
import storage

class storage_file(storage.storage):
    filename = 'inventory_data'

    def __init__(self):
        try:
            with open(self.filename,"rb" ) as file:
                file_json = file.read()
                self.myDic = json.loads(file_json)
        except:
            self.myDic = {}


    def increaseDecrease(self, temporary_dic, k, v):
        #removes the starting + or minus
        value_part = v[1:]
        try:
            value_int = int( value_part )
        except:
            raise storage.InventoryException('400 Bad Request', \
            'Cannot convert quantity to integer ')

        if k not in self.myDic:
            raise storage.InventoryException("404 Not Found" , \
            "Cannot increase or decrease non-existent item(s) in the inventory")
        ori_v = self.myDic[k]
        new_v = 0
        if v.startswith("+"):
            new_v = ori_v + value_int
        #v starts with "-"
        else:
            new_v = ori_v - value_int
            if new_v <0:
                raise storage.InventoryException("400 Bad Request"," \
                Cannot have negative quantities")
        temporary_dic[k] = new_v
        return temporary_dic

    #return a dictionary of succesfully updated item and quantity
    def update(self, dict):
        temporary_dic = {}
        for k, v in dict.items():
            if isinstance(v, int):
                if v<0:
                    raise storage.InventoryException("400 Bad Request",\
                    "Cannot have negative quantities")
                temporary_dic[k] = v
            elif  v.startswith("+") or v.startswith("-"):
                try:
                    temporary_dic = self.increaseDecrease(temporary_dic, k, v)
                except storage.InventoryException as ex:
                    raise storage.InventoryException(ex)
            else: #quantity string does not start with "+" or "-" sign,
                try:
                    intg = int(v)
                except:
                    raise storage.InventoryException("400 Bad Request",\
                    "Cannot convert quantity to integer")
                temporary_dic[k] = intg

        self.myDic.update(temporary_dic)
        return temporary_dic

    def remove(self, key):
        try:
            self.myDic.pop(key)
        except:
            raise storage.InventoryException('404 Not Found', \
            'No such item in the inventory')

    def get(self, key):
        try:
            value = self.myDic[key]
            return value
        except:
            raise storage.InventoryException('404 Not Found',\
             'No such item in the inventory')

    def getAll(self):
        return self.myDic

    def boundSearch(self, upperBound_str, lowerBound_str):
        try:
            upperBound_int=self.boundToInt(upperBound_str)
            lowerBound_int=self.boundToInt(lowerBound_str)
        except storage.InventoryException as ex:
            raise storage.InventoryException(ex)
        result_dic = {}
        for k, v in self.myDic.items():
            fulfilled = True
            if upperBound_int !=None:
                if v > upperBound_int:
                    fulfilled = False
            if lowerBound_int !=None:
                if v < lowerBound_int:
                    fulfilled = False
            if(fulfilled):
                result_dic[k]=v
        return result_dic

    @staticmethod
    def boundToInt(bound_str):
        bound_int = None
        if isinstance(bound_str, int):
            bound_int = bound_str
        elif bound_str != None:
            try:
                bound_int = int(bound_str)
            except:
                raise storage.InventoryException('400 Bad Request', \
                'Invalid Boundary input,\
                    must be whole numbers')
        return bound_int

    def save(self):
        myDic_json = json.dumps(self.myDic)
        with open(self.filename, "w+") as file:
            file.write(myDic_json)
