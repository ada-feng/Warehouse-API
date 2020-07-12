from abc import ABC,  abstractmethod

class InventoryException( Exception):
    status = ''
    message = ''

    def __init__(self, statusORcopy, message =None):
        if message==None:
            self.status = statusORcopy.status
            self.message =statusORcopy.message
        else:
            self.status = statusORcopy
            self.message =message

class storage(ABC):

    @abstractmethod
    def __init__(self):
        pass

    #return a dictionary of succesfully updated item and quantity
    @abstractmethod
    def update(self, dict):
        pass

    #return None
    @abstractmethod
    def remove(self, key):
        pass

    #return an integer
    @abstractmethod
    def get(self, key):
        pass


    #return the whole storage as a dictionary
    @abstractmethod
    def getAll(self):
        pass

    #return a dictionary of values and
    #quantity matching the boundary search
    @abstractmethod
    def boundSearch(self, upperBound_str, lowerBound_str):
        pass

    @staticmethod
    def boundToInt(bound_str):
        bound_int = None
        if isinstance(bound_str, int):
            bound_int = bound_str
        elif bound_str != None:
            try:
                bound_int = int(bound_str)
            except:
                raise InventoryException('400 Bad Request', 'Invalid Boundary input,\
                    must be whole numbers')
        return bound_int

    @abstractmethod
    def save(self):
        pass
