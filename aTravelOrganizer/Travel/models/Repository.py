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

                if first_line:
                    user_obj = User(first_line[1], first_line[0], first_line[3], first_line[4], 1)  # email, password, first_name, last_name
                    
                    ###  REMOVE LATER END
                    return user_obj
                else:
                    return None                

        except Exception as e:
            print("Error Occured in Repository.get_password" + str(e) )
            # prompt to create an account with the email(==user id)
            raise


    ### WORKING :D **************************************************************************
    def update_user(self, user_obj, user_id):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                cursor.execute("UPDATE users SET user_id=?, user_pw=?, fname=?, lname=? WHERE user_id = ?", (user_obj.email, user_obj.pw_hash, user_obj.fname, user_obj.lname, user_id))
        except Exception as e:
            print("Error Occured in Repository.update_user" + str(e))
            raise
        pass        



    def create_user(self, user_obj):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                cursor.execute("insert into users (user_id, user_pw, fname, lname) values (?, ?, ?, ?)", (user_obj.email, user_obj.pw_hash, user_obj.fname, user_obj.lname))
        except Exception as e:
            print("Error Occured in Repository.create_user" + str(e))
            raise


    def get_admin_user_id(self, trip_id):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                exe = cursor.execute("select user_id_s from trips where trip_id = ?", (trip_id,))
                first_line = exe.fetchone()
                
                user_id = None
                if first_line and first_line[0]:
                    user_id = first_line[0]


                return user_id

        except Exception as e:
            print("Error Occured in Repository.get_admin_user_id" + str(e) )
            raise

        pass

    # return True if trip_id is existing in table 'trips'
    def check_exist_trip(self, existing_trip_id):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                exe = cursor.execute("select * from trips where trip_id=?", (existing_trip_id,))
                first_line = exe.fetchone()

                if first_line:
                    return True                    
                else:
                    return False
                    
                
        except Exception as e:
            print("Error Occured in Repository.check_exist_trip" + str(e) )
            raise

        pass


    def add_trip_name(self, trip_obj, admin):  # arg 'admin' is boolean
        try:
            with self.__conn:
                cursor = self.__conn.cursor()                
                
                if admin:
                    cursor.execute("insert into trips (trip_id, trip_name, user_id_s, start_datetime, end_datetime) values (?, ?, ?, ?, ?)", (trip_obj.trip_id, trip_obj.trip_name, trip_obj.user_id, trip_obj.start_datetime, trip_obj.end_datetime))  
                    column = "trip_admin"                    
                else:
                    column = "trip_user"
                    
                trip_admin = cursor.execute("select " + column + " from users where user_id = ?", (trip_obj.user_id,))
                trip_result = trip_admin.fetchone()

                trip_str = ''

                if trip_result[0] is None or trip_result[0] == '' :
                    trip_str = trip_obj.trip_id
                else:                    
                    trip_result_list = []
                    trip_result_list.append(trip_result[0])
                    trip_result_list.append(trip_obj.trip_id)
                
                    trip_str = ', '.join(trip_result_list)                    

                if admin:
                    cursor.execute("UPDATE users SET trip_admin=? WHERE user_id=?", (trip_str, trip_obj.user_id))                
                    pass
                else:
                    cursor.execute("UPDATE users SET trip_user=? WHERE user_id=?", (trip_str, trip_obj.user_id))                
                    pass
                
                

        except Exception as e:
            print("Error Occured in Repository.add_trip_name" + str(e))
            raise
    

    def get_trip_name(self, trip_id):
        try:
            cursor = self.__conn.cursor()
            exe = cursor.execute("select trip_name from trips where trip_id= ?", (trip_id,) )  
            result = exe.fetchone()

            if result and result[0]:
                return result[0]
            else:
                None

        except Exception as e:
            print("ERROR OCCURED in Repository.get_trip_name: " + str(e))
            raise
            



    def get_trips_from_trips_table(self, trip_id):
        try:
            
            list_all = []

            cursor = self.__conn.cursor()
            exe = cursor.execute("select trip_id, trip_name, user_id_s, start_datetime, end_datetime	from trips where trip_id= ?", (trip_id,) )   # user_id = ?", (user_id,)
            result = exe.fetchone()

            if result:
                list_all.extend(result)
            else:
                list_all = []

            return list_all
        except Exception as e:
            print("ERROR OCCURED in Repository.get_trips_from_trips_table: " + str(e))
            raise





    def get_trips(self):
        try:
            
            list_all = []

            cursor = self.__conn.cursor()
            exe = cursor.execute("select * from trips")
            result = exe.fetchall()
            list_all.extend(result)

            return list_all
        except Exception as e:
            print("ERROR OCCURED in Repository.get_trips....shhhh...: " + str(e))
            raise

    def get_trip_datetime_start(self, event_obj):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                exe = cursor.execute("select start_datetime from trips where trip_id = ?", (event_obj.travel_id,))
                # event_obj.travel_id, event_obj.datetime 
                first_line = exe.fetchone()

                if first_line and first_line[0]:
                    return first_line[0]
                else:
                    return None

        except Exception as e:
            print("Error OCCURED in Repository.get_trip_datetime_start : " + str(e))
            raise
        pass

    def get_trip_datetime_end(self, event_obj):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                exe = cursor.execute("select end_datetime from trips where trip_id = ?", (event_obj.travel_id,))
                # event_obj.travel_id, event_obj.datetime 
                first_line = exe.fetchone()

                if first_line and first_line[0]:
                    return first_line[0]
                else:
                    return None
        except Exception as e:
            print("Error OCCURED in Repository.get_trip_datetime_end : " + str(e))
            raise
        pass

    def update_trip_datetime_start(self, datetime, travel_id):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                exe = cursor.execute("UPDATE trips SET start_datetime=? WHERE trip_id=?", (datetime, travel_id))                
                pass
        except Exception as e:
            print("Error OCCURED in Repository.update_trip_datetime_start : " + str(e))
            raise
        pass

    def update_trip_datetime_end(self, datetime, travel_id):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                exe = cursor.execute("UPDATE trips SET end_datetime=? WHERE trip_id=?", (datetime, travel_id))                
                pass
        except Exception as e:
            print("Error OCCURED in Repository.update_trip_datetime_end : " + str(e))
            raise
        pass

    # ADD EVENT OBJ : Flight
    def add_flight(self, flight_obj):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                cursor.execute("insert into Flight (travel_id, title, datetime, flight_info, live_status) values(?, ?, ?, ?, ?)", (flight_obj.travel_id, flight_obj.title, flight_obj.datetime, flight_obj.info, flight_obj.status))
                
        except Exception as e:
            print("ERROR OCCURED in Repository.add_flight: " + str(e) )
            raise
        return

    # ADD EVENT OBJ : Hotel
    def add_hotel(self, hotel_obj):
        try:
            with self.__conn:
                cursor = self.__conn.cursor()
                cursor.execute("insert into Hotel (travel_id, title, datetime, hotel_info) values(?, ?, ?, ?)", (hotel_obj.travel_id, hotel_obj.title, hotel_obj.datetime, hotel_obj.info))
        except Exception as e:
            print("ERROR OCCURED in Repository.add_hotel: " + str(e) )
            raise
        return

    # ADD EVENT OBJ : Place
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


    def get_trip_users(self, user_id):  # return non-admin trip ids
        try:
            cursor = self.__conn.cursor()
            user_list = []
            
            trip_user = cursor.execute("select trip_user from users where user_id = ?", (user_id,))
            user_result = trip_user.fetchone()

            if admin_result is None:
                return None

            user_s = str(user_result[0])

            # comma separated string to list
            pattern = re.compile("^\s+|\s*,\s*|\s+$")
            user_list = [x for x in pattern.split(admin_s) if x]

            return user_list  # type: list

        except Exception as e:
            # Do something here
            print("ERROR OCCURED in Repository.get_trip_users:" +  str(e) )
            raise
        return


    # get trip_admin trip ids from users and return all the admin : TRIP IDs
    def get_trip_list(self, user_id, admin): 
        try:
            cursor = self.__conn.cursor()
            trip_list = []
            
            if admin:
                column = "trip_admin"
            else:
                column = "trip_user"
            
            

            trip_admin = cursor.execute("select " + column + " from users where user_id = ?", (user_id,))
            admin_result = trip_admin.fetchone()

            if admin_result is None:
                return None

            admin_s = str(admin_result[0])

            # comma separated string to list
            pattern = re.compile("^\s+|\s*,\s*|\s+$")
            trip_list = [x for x in pattern.split(admin_s) if x]

            return trip_list

        except Exception as e:
            # Do something here
            print("ERROR OCCURED in Repository.get_trip_list:" +  str(e) )
            raise
        return




    def get_travel_events(self, travel_id):
        try:
            cursor = self.__conn.cursor()
            list_all = []

            exe = cursor.execute("select title, flight_info, datetime, live_status from Flight where travel_id = ? ", (travel_id,))
            result = exe.fetchall()
            if result and result[0]:
                list_all.extend(result)

            exe = cursor.execute("select title, hotel_info, datetime from Hotel where travel_id = ? ", (travel_id,))
            result = exe.fetchall()
            if result and result[0]:
                list_all.extend(result)

            exe = cursor.execute("select title, place_info, datetime from Place where travel_id = ? ", (travel_id,))
            result = exe.fetchall()
            if result and result[0]:
                list_all.extend(result)




            # fetchone() --> get only the first line

            print(list_all)  # print tuple here

            
            return list_all
        except Exception as e:
            # Do something here
            print("ERROR OCCURED in Repository.get_travel_events:" +  str(e) )
            raise
        return