import sqlite3
import re
from Travel.models.User import User
from werkzeug.security import generate_password_hash

class Repository(object):

    def __init__(self, connectionString):
        self.__conn = sqlite3.connect(connectionString, check_same_thread=False)
        # self.__conn = sqlite3.connect(r'C:\Users\junes\OneDrive\Documents\Visual Studio 2015\Projects\pythonProject\TravelPlanner\TravelPlanner\data.sqlite')

    def __del__(self):
        self.__conn.close()

    def get_user_obj(self, email):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                exe = cursor.execute("select user_pw, user_id, user_pw, fname, lname from users where user_id = ?", (email,))
                first_line = exe.fetchone()


                ### REMOVE LATER START
                print("password = " + str(first_line[0]))
                print("password[0] = " + str(first_line[0]))
                
                for i in first_line:
                    print("first_line===================================")
                    print(i)

                user_obj = User(first_line[1], first_line[0], first_line[3], first_line[4], 1)  # email, password, first_name, last_name
                print("user_obj: ")
                print(user_obj)
                ###  REMOVE LATER END


                return user_obj

        except Exception as e:
            print("Error Occured in Repository.get_password" + str(e) )
            # prompt to create an account with the email(==user id)
            raise

        

    def create_user(self, user_obj):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                cursor.execute("insert into users (user_id, user_pw, fname, lname) values (?, ?, ?, ?)", (user_obj.email, user_obj.pw_hash, user_obj.fname, user_obj.lname))
        except Exception as e:
            print("Error Occured in Repository.create_user" + str(e))
            raise

    def add_trip_name(self, trip_obj):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                cursor.execute("insert into trips (trip_id, trip_name, user_id_s) values (?, ?, ?)", (trip_obj.trip_id, trip_obj.trip_name, trip_obj.user_id))  
                
                ### add new trip to the user
                trip_admin = cursor.execute("select trip_admin from users where user_id = ?", (trip_obj.user_id,))
                admin_result = trip_admin.fetchone()
                admin_list = []
                admin_list.append(admin_result[0])
                admin_list.append(trip_obj.trip_id)
                
                admin_s = ', '.join(admin_list)
                cursor.execute("UPDATE users SET trip_admin=? WHERE user_id=?", (admin_s, trip_obj.user_id))



        except Exception as e:
            print("Error Occured in Repository.add_trip_name" + str(e))
            raise


    def get_admin_trips(self, trip_id):
        try:
            
            list_all = []

            cursor = self.__conn.cursor()
            exe = cursor.execute("select * from trips where trip_id= ?", (trip_id,) )   # user_id = ?", (user_id,)
            result = exe.fetchone()
            list_all.extend(result)

            print(list_all)
            return list_all
        except Exception as e:
            print("ERROR OCCURED in Repository.get_trips: " + str(e))
            raise





    def get_trips(self):
        try:
            
            list_all = []

            cursor = self.__conn.cursor()
            exe = cursor.execute("select * from trips")
            result = exe.fetchall()
            list_all.extend(result)

            print(list_all)
            return list_all
        except Exception as e:
            print("ERROR OCCURED in Repository.get_trips: " + str(e))
            raise


    def add_flight(self, flight_obj):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                cursor.execute("insert into Flight (travel_id, title, datetime, flight_info, live_status) values(?, ?, ?, ?, ?)", (flight_obj.travel_id, flight_obj.title, flight_obj.datetime, flight_obj.info, flight_obj.status))
        except Exception as e:
            print("ERROR OCCURED in Repository.add_flight: " + str(e) )
            raise
        return

    def add_hotel(self, hotel_obj):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                cursor.execute("insert into Hotel (travel_id, title, datetime, hotel_info) values(?, ?, ?, ?)", (hotel_obj.travel_id, hotel_obj.title, hotel_obj.datetime, hotel_obj.info))
        except Exception as e:
            print("ERROR OCCURED in Repository.add_hotel: " + str(e) )
            raise
        return

    def add_place(self, place_obj):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                cursor.execute("insert into Place (travel_id, title, datetime, place_info) values(?, ?, ?, ?)", (place_obj.travel_id, place_obj.title, place_obj.datetime, place_obj.info))
        except Exception as e:
            print("ERROR OCCURED in Repository.add_place: " + str(e) )
            raise
        return



##########################################################################################
    ## OLD START ##
    def add_travel_info(self, flight_obj, hotel_obj, place_obj):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                cursor.execute("insert into Flight (travel_id, title, datetime, flight_info, live_status) values(?, ?, ?, ?, ?)", (flight_obj.travel_id, flight_obj.title, flight_obj.datetime, flight_obj.info, flight_obj.status))
                cursor.execute("insert into Hotel (travel_id, title, datetime, hotel_info) values(?, ?, ?, ?)", (hotel_obj.travel_id, hotel_obj.title, hotel_obj.datetime, hotel_obj.info))
                cursor.execute("insert into Place (travel_id, title, datetime, place_info) values(?, ?, ?, ?)", (place_obj.travel_id, place_obj.title, place_obj.datetime, place_obj.info))
        except Exception as e:
            print("ERROR OCCURED in Repository.add_travel_info: "+ e)
            # Do something here
            raise


    def get_trip_users(self, user_id):
        try:
            cursor = self.__conn.cursor()
            user_list = []
            
            trip_user = cursor.execute("select trip_user from users where user_id = ?", (user_id,))
            user_result = trip_user.fetchone()
            user_s = str(user_result[0])

            # comma separated string to list
            pattern = re.compile("^\s+|\s*,\s*|\s+$")
            user_list = [x for x in pattern.split(admin_s) if x]

            return user_list

        except Exception as e:
            # Do something here
            print("ERROR OCCURED in Repository.get_travel_events:" +  str(e) )
            raise
        return



    def get_trip_admins(self, user_id):
        try:
            cursor = self.__conn.cursor()
            admin_list = []
            
            trip_admin = cursor.execute("select trip_admin from users where user_id = ?", (user_id,))
            admin_result = trip_admin.fetchone()
            admin_s = str(admin_result[0])

            # comma separated string to list
            pattern = re.compile("^\s+|\s*,\s*|\s+$")
            admin_list = [x for x in pattern.split(admin_s) if x]

            return admin_list

        except Exception as e:
            # Do something here
            print("ERROR OCCURED in Repository.get_travel_events:" +  str(e) )
            raise
        return




    def get_travel_events(self, travel_id):
        try:
            cursor = self.__conn.cursor()
            list_all = []

            for each in ["Flight","Hotel","Place"]:
                exe = cursor.execute("select * from " + each + " where travel_id = ?", (travel_id,))
                result = exe.fetchall()
                list_all.extend(result)


            # fetchone() --> get only the first line

            print(list_all)  # print tuple here

            
            return list_all
        except Exception as e:
            # Do something here
            print("ERROR OCCURED in Repository.get_travel_events:" +  str(e) )
            raise
        return