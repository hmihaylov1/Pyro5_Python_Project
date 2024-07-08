import sys
import Pyro5.errors
from Pyro5.api import Proxy

# Check that the Python file rental.py exists.
import os.path
if(os.path.isfile("rental.py")==False):
	print("Error you need to call the Python file rental.py!")

# Check that the class is called rental. That is, the file rental.py contains the expression "rental(object):"
file_text = open('rental.py', 'r').read()
if("rental(object):" not in file_text):
	print("Error you need to call the Python class rental!")

sys.excepthook = Pyro5.errors.excepthook
rental_object = Proxy("PYRONAME:example.rental")

rental_object.add_user("Conor Reilly", "123456")
print(rental_object.return_users())
rental_object.add_manufacturer("BMW", "Germany")
print(rental_object.return_manufacturers())
rental_object.add_rental_car("BMW", "3 Series")
print(rental_object.return_cars_not_rented())
rental_object.rent_car("Conor Reilly", "3 Series", 2019, 1, 3)
print(rental_object.return_cars_rented())
rental_object.end_rental("Conor Reilly", "3 Series", 2019, 2, 4)
rental_object.delete_car("3 Series")
rental_object.delete_user("Conor Reilly")
print(rental_object.user_rental_date("Conor Reilly", 2010, 1, 1, 2029, 2, 1))
