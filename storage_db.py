from storage import InventoryException as IvEx
import storage
import sqlite3

class storage_db(storage.storage):
    con = sqlite3.connect("storage.db", isolation_level=None)
    cur = con.cursor()

    def __init__(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS Inventory
                        ( name TEXT PRIMARY KEY,
                         quantity INTEGER NOT NULL );''')

    def insertNew(self, k, v):
        params= (k,v)
        self.cur.execute("INSERT OR REPLACE INTO Inventory VALUES (?, ?)", params)
        params =(v,k)
        self.cur.execute("UPDATE Inventory SET quantity = ? WHERE quantity LIKE ?;", params)

    def increaseDecrease(self, k, v):
        #removes the starting + or minus
        value_part = v[1:]
        try:
            value_int = int( value_part )
        except:
            raise IvEx('400 Bad Request', \
            'Cannot convert quantity to integer ')
        try:
            ori_v = self.get(k)
        except:
            raise IvEx("404 Not Found" , \
            "Cannot increase or decrease non-existent item(s) in the inventory")
        params = (value_int, k)
        if v.startswith("-"):
            new_v = ori_v - value_int
            if new_v <0:
                raise IvEx("400 Bad Request"," \
                Cannot have negative quantities")
            self.cur.execute("Update Inventory SET quantity = quantity-? WHERE name = ?", params)
        else:
            self.cur.execute("Update Inventory SET quantity = quantity+? WHERE name = ?", params)
        new_v = self.get(k)
        return new_v


    #return a dictionary of succesfully updated item and quantity
    def update(self, dict):
        dic = {}
        self.cur.execute("BEGIN TRANSACTION")
        for k, v in dict.items():
            if isinstance(v, int):
                if v<0:
                    raise IvEx("400 Bad Request",\
                    "Cannot have negative quantities")
                else:
                    try:
                        self.insertNew(k,v)
                    except IvEx as ex:
                        raise IvEx(ex)
                    dic[k] = v
            elif  v.startswith("+") or v.startswith("-"):
                try:
                    new_v = self.increaseDecrease( k, v )
                except IvEx as ex:
                    raise IvEx(ex)
                dic[k] = new_v
            else: #quantity string does not start with "+" or "-" sign,
                try:
                    int_v = int(v)
                except:
                    raise IvEx("400 Bad Request",\
                    "Cannot convert quantity to integer")
                try:
                    self.insertNew( k , int_v)
                    dic[k] = int_v
                except IvEx as ex:
                    raise IvEx(ex)

        self.cur.execute("END TRANSACTION")
        return dic

    def remove(self, key):
        try:
            value = self.get(key)
        except IvEx as ex:
            raise IvEx(ex)
        self.cur.execute("DELETE from Inventory where name = ?",(key,))

    def get(self, key):
        self.cur.execute("SELECT quantity FROM Inventory WHERE name = ?", (key,))
        try:
            value = self.cur.fetchone()[0]
        except:
            raise IvEx('404 Not Found', 'No such item in the inventory')
        return value

    def getAll(self):
        dic = {}
        self.cur.execute("SELECT * FROM Inventory")
        all_list=self.cur.fetchall()
        for row in all_list:
            key = row[0]
            value = row[1]
            dic[key] = value
        return dic

    def boundSearch(self, upperBound_str, lowerBound_str):
        try:
            upperBound_int=self.boundToInt(upperBound_str)
            lowerBound_int=self.boundToInt(lowerBound_str)
        except IvEx as ex:
            raise IvEx(ex)
        if upperBound_int==None and lowerBound_int!=None:
            self.cur.execute("SELECT * FROM Inventory where quantity>=?", (lowerBound_int,))
        elif upperBound_int!=None and lowerBound_int==None:
            self.cur.execute("SELECT * FROM Inventory where quantity<=?", (upperBound_int,))
        elif upperBound_int!=None and lowerBound_int!=None:
            params = (lowerBound_int, upperBound_int)
            self.cur.execute("SELECT * FROM Inventory where quantity>=? AND quantity<=?",\
            params)
        else:
            self.cur.execute("SELECT * FROM Inventory")
        dic ={}
        all_list=self.cur.fetchall()
        for row in all_list:
            key = row[0]
            value = row[1]
            dic[key] = value
        return dic

    @staticmethod
    def boundToInt(bound_str):
        bound_int = None
        if isinstance(bound_str, int):
            bound_int = bound_str
        elif bound_str != None:
            try:
                bound_int = int(bound_str)
            except:
                raise IvEx('400 Bad Request', 'Invalid Boundary input,\
                    must be whole numbers')
        return bound_int

    def save(self):
        self.con.commit()
