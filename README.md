# Warehouse-API
For web services class
Look at warehouse_api.txt for available http requests and valid url queries

functions:
1. Add one or more items to the inventory and their corresponding initial quantities in the inventory. The server should not accept negative quantity. If an item already exists in the inventory, the service should replace its existing quantity with the new quantity.

2. Retrieve the quantity of item in the inventory
3. Remove an item from the inventory

versions:
(in the command line)
-f for storing the inventory in a file;
-d for storing in a sqlite database;
default: database
