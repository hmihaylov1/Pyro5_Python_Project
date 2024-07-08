from Pyro5.api import expose, behavior, serve, Daemon
from collections import namedtuple
import datetime
from datetime import date

User = namedtuple("User", ["name", "number"])
Manufacturer = namedtuple("Manufacturer", ["name", "country"])
RentalCar = namedtuple("RentalCar", ["manufacturer_name", "car_model"])
RentalRecord = namedtuple("RentalRecord", ["user_name", "car_model", "rental_date"])

@expose
@behavior(instance_mode="single")
class rental(object):
    def __init__(self):
        self.users = []
        self.manufacturers = []
        self.rental_cars = []
        self.rental_records = []
        self.rental_history = []

    def add_user(self, user_name, user_number):
        if not isinstance(user_name, str) or not isinstance(user_number, str):
            return "User name and number must be strings."

        for user in self.users:
            if user.name == user_name:
                print("User with username '{}' already exists. User Not Added!".format(user_name))
                return "User with username '{}' already exists. User Not Added!".format(user_name)

        new_user = User(user_name, user_number)
        self.users.append(new_user)
        print("User '{}' Added Successfully!".format(user_name))
        return "User '{}' Added Successfully!".format(user_name)

    def return_users(self):
        if not self.users:
            return "No users registered."

        formatted_users = []
        for user in self.users:
            formatted_user = (
                f"Username: {user.name}, "
                f"User Number: {user.number}"
            )
            formatted_users.append(formatted_user)

        return "\n".join(formatted_users)

    def add_manufacturer(self, manufacturer_name, manufacturer_country):
        if not isinstance(manufacturer_name, str) or not isinstance(manufacturer_country, str):
            return "Manufacturer name and country must be strings."

        for manufacturer in self.manufacturers:
            if manufacturer.name == manufacturer_name:
                print("Manufacturer with name '{}' already exists. Manufacturer Not Added!".format(manufacturer_name))
                return "Manufacturer with name '{}' already exists. Manufacturer Not Added!".format(manufacturer_name)
        new_manufacturer = Manufacturer(manufacturer_name, manufacturer_country)
        self.manufacturers.append(new_manufacturer)
        print("Manufacturer '{}' Added Successfully!".format(manufacturer_name))
        return "Manufacturer '{}' Added Successfully!".format(manufacturer_name)

    def return_manufacturers(self):
        if not self.manufacturers:
            return "No manufacturers registered."

        formatted_manufacturers = []
        for manufacturer in self.manufacturers:
            formatted_manufacturer = (
                f"Manufacturer Name: {manufacturer.name}, "
                f"Country: {manufacturer.country}"
            )
            formatted_manufacturers.append(formatted_manufacturer)

        return "\n".join(formatted_manufacturers)

    def add_rental_car(self, manufacturer_name, car_model):
        if not isinstance(manufacturer_name, str) or not isinstance(car_model, str):
            return "Manufacturer name and car model must be strings."

        manufacturer_exists = any(manufacturer.name == manufacturer_name for manufacturer in self.manufacturers)
        if not manufacturer_exists:
            print("Manufacturer '{}' does not exist. Car Not Added!".format(manufacturer_name))
            return "Manufacturer '{}' does not exist. Car Not Added!".format(manufacturer_name)

        new_car = RentalCar(manufacturer_name, car_model)

        self.rental_cars.append(new_car)
        print("Rental Car '{}' by '{}' Added Successfully!".format(car_model, manufacturer_name))
        return "Rental Car '{}' by '{}' Added Successfully!".format(car_model, manufacturer_name)

    def return_cars_not_rented(self):
        if not self.rental_cars:
            return "No cars available for rent."

        formatted_cars = []
        for car in self.rental_cars:
            formatted_car = (
                f"Manufacturer: {car.manufacturer_name}, "
                f"Car Model: {car.car_model}"
            )
            formatted_cars.append(formatted_car)

        return "\n".join(formatted_cars)

    def rent_car(self, user_name, car_model, year, month, day):
        user_exists = any(user.name == user_name for user in self.users)
        if not user_exists:
            print("User '{}' does not exist. Car Not Rented!".format(user_name))
            return 0

        car_available_index = None
        for i, car in enumerate(self.rental_cars):
            if car.car_model == car_model:
                car_available_index = i
                break
        if car_available_index is None:
            print("Car '{}' is not available for rent. Car Not Rented!".format(car_model))
            return 0

        car_rented = any(record.car_model == car_model for record in self.rental_records)
        if car_rented:
            print("Car '{}' is already rented. Car Not Rented!".format(car_model))
            return 0

        try:
            rental_date = datetime.date(year, month, day)
        except ValueError:
            print("Invalid rental date. Car Not Rented!")
            return 0

        rental_record = RentalRecord(user_name, car_model, rental_date)
        self.rental_records.append(rental_record)

        del self.rental_cars[car_available_index]

        print("Car '{}' rented to '{}' on {} successfully.".format(car_model, user_name, rental_date))
        return 1

    def return_cars_rented(self):
        rented_cars_info = []

        for record in self.rental_records:
            # Format each record's information as a tuple
            rented_car_info = (
                record.car_model,
                record.user_name,
                record.rental_date.strftime('%Y-%m-%d')
            )
            rented_cars_info.append(rented_car_info)

        return rented_cars_info

    def end_rental(self, user_name, car_model, end_year, end_month, end_day):
        end_date = date(end_year, end_month, end_day)

        # Find the rental record to end based on user_name and car_model
        found_record = None
        for record in self.rental_records:
            if record.user_name == user_name and record.car_model == car_model:
                found_record = record
                break

        if not found_record:
            print(f"No active rental found for user '{user_name}' with car model '{car_model}'.")
            return 0

        if end_date <= found_record.rental_date:
            print("End Date has to be before the Rental Date. Rental not ended.")
            return 0

        # Simulate returning the rental car by adding it back to self.rental_cars
        returned_car = RentalCar(found_record.car_model, found_record.car_model)
        self.rental_cars.append(returned_car)
        print(returned_car)
        self.rental_history.append({"username" : user_name,
                                    "car_model" : car_model,
                                    "rental_date" : found_record.rental_date,
                                    "end_date" : end_date})

        print(f"Rental for user '{user_name}' with car model '{car_model}' ended successfully on {end_date}.")
        return 1

    def delete_car(self, car_model):
        cars_to_delete = []
        for car in self.rental_cars:
            if car.car_model == car_model:
                car_rented = any(record.car_model == car_model for record in self.rental_records)
                if not car_rented:
                    cars_to_delete.append(car)

        for car in cars_to_delete:
            self.rental_cars.remove(car)

        print("Deleted non-rented cars of model '{}'.".format(car_model))

    def delete_user(self, user_name):
        # Check if the user exists
        user_exists = any(user.name == user_name for user in self.users)
        if not user_exists:
            print("User '{}' does not exist.".format(user_name))
            return 0

        # Check if the user has rented any cars
        rented_cars_info = self.return_cars_rented()
        for car_info in rented_cars_info:
            if car_info[1] == user_name:  # Check the user_name in the tuple
                print("User '{}' cannot be deleted as they have rented a car.".format(user_name))
                return 0

        # If the user has not rented any cars, delete the user
        for user in self.users:
            if user.name == user_name:
                self.users.remove(user)
                print("User '{}' has been deleted.".format(user_name))
                return 1

        # If user not found, print error message and return 0
        print("User '{}' not found.".format(user_name))
        return 0

    def user_rental_date(self, user_name, start_year, start_month, start_day, end_year, end_month, end_day):
        start_date = date(start_year, start_month, start_day)
        end_date = date(end_year, end_month, end_day)

        user_records = []
        for record in self.rental_history:
            if record["username"] == user_name:
                rental_date = record["rental_date"]
                end_date_recorded = record["end_date"]
                if start_date <= rental_date <= end_date:
                    user_records.append((record["car_model"], rental_date, end_date_recorded))

        if not user_records:
            return f"No rental records found for user '{user_name}' within the specified date range."

        formatted_records = []
        for car_model, rental_date, end_date_recorded in user_records:
            formatted_record = (
                f"Username: {user_name}, "
                f"Car Model: {car_model}, "
                f"Rental Date: {rental_date}, "
                f"End Date: {end_date_recorded}"
            )
            formatted_records.append(formatted_record)

        return "\n".join(formatted_records)


daemon = Daemon()
serve({rental: "example.rental"}, daemon=daemon, use_ns=True)