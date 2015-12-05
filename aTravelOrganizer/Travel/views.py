from flask import Flask, url_for, request, render_template, redirect, flash, session
from bs4 import BeautifulSoup
import json, requests

from Travel import app
from Travel import repo
from Travel import app_user
from Travel.models.Flight import Flight
from Travel.models.Hotel import Hotel
from Travel.models.Place import Place
from Travel.models.trip import Trip
from Travel.models.User import User
from werkzeug.security import generate_password_hash

import datetime
from jinja2 import Template
from bs4.builder import HTML
from flask import Markup
from datetime import datetime
import re

def requires_permissions(*permissions):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if repo.get_user(session['username']).permissions in permissions:
                return f(*args, **kwargs)
            else:
                abort(403)
        return wrapped
    return wrapper

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_user' in session:
            return f(*args, **kwargs)
        else:
            flash("A login is required to see the page!")
            return redirect(url_for('login', next=request.path))
    return decorated_function






# global variable
# app_user = None

# global variables -- temp
travel_id = "ok whatever"
user_id = "user_js_01"
user_name = "happy tree"
trip_id = "default"

@app.route('/')  # temp --> remove later
@app.route('/logout')
def logout():
    print("logout !!!")
    session.pop('session_user', None)
    session.pop('logged_in', None)
    return redirect(url_for('login'))  



### *********************************************************************************************************************
### #######################################                 ROOT PAGE                 ####################################
### *********************************************************************************************************************
# @app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods =['GET','POST'])
def login():
    # global app_user
    # session required

    if request.method == 'GET' and session.get('session_user') is None :
        print("BOTH == NONE")
        return render_template('login.html')
    else:
        user_email = request.form['login_email']
        user_pw = request.form['login_pw']

        ### after having useremail && password 
        login_user = repo.get_user_obj(user_email)

        if login_user.check_password(user_pw):
            session['session_user'] = user_email
            session['logged_in'] = True
            app_user.reset_all(login_user.email, login_user.pw_hash, login_user.fname, login_user.lname)
            return redirect(url_for('home'))  
        else:
            flash("Username or password was incorrect")
            return redirect(url_for('login')) 

        ### when the user wants to create an account
        if request.form['auth'] == 'create_account':
            print('create_account--- form has been sent :D')

            # TO-DO : validation of the form is required EACH
            email = request.form['create_login_email'] 
            pw = request.form['create_login_pw']   
            fname = request.form['create_account_fname']
            lname = request.form['create_account_lname']

            temp_user = User(email, pw, fname, lname, 0)
            repo.create_user(temp_user)             
            
            return render_template('login.html', message=Markup("<div style='color:#f00;'>Thank you for create an account! </div>"))
        pass
        

### *********************************************************************************************************************
### #######################################                 HOME PAGE                 ####################################
### *********************************************************************************************************************
@app.route('/home', methods=['GET', 'POST'])
def home():
    # global app_user
    global trip_id

    if 'logout' in request.form:
        session.pop('username', None)
        return redirect(url_for('start'))

    

    if request.method == 'GET': 

        if session.get('logged_in') and session['logged_in'] == True :
            trip_id = get_auto_gen_trip_id( str(datetime.utcnow()), app_user.get_email())

            trips_output = [] # set empty str
            admin_result = repo.get_trip_list(app_user.get_email(), True)  # list of admin trip_id(s) in 'user' table
            user_result = repo.get_trip_list(app_user.get_email(), False)  # list of user trip_id(s) in 'user' table
            

            if not admin_result or admin_result[0] == 'None' :
                pass
            else:
                ## 'admin_list' from Database Table 'trips' to table view (html)
                admin_list = []
                for each in admin_result:
                    admin_list.append(repo.get_trips_from_trips_table(each))
                trips_output.append(get_trips_in_table(admin_list, True))
                pass

            if not user_result or user_result[0] == 'None':
                pass
            else:
                ## 'user_list' from Database Table 'trips' to table view (html)
                user_list = []
                for each in user_result:
                    user_list.append(repo.get_trips_from_trips_table(each))
                trips_output.append(get_trips_in_table(user_list, False))
                pass

            trips_output = Markup(" ".join(trips_output))

            return render_template(
            'index.html',
            title='Home Page',
            user_name = app_user.get_fname() ,
            travel_id = travel_id,
            auto_gen_trip_id = trip_id,
            show_trip_list = trips_output,
            year=datetime.now().year
            )
            pass
        else:
            print("failed to auth handling")
            pass

    elif request.method == 'POST':  

        
        ## Add Existing Trip_id from aother user
        if request.form['new_trip'] == 'add_existing':
            print("[new_trip] = add_existing")
            
            # invalid input handling (TO DO)
            existing_trip_id = request.form['existing_trip_id']  # from form
            t = Trip(existing_trip_id, 'trip_name', app_user.get_email())  # trip_id, trip_name, user_id(email)
            repo.add_trip_name(t, False)
            

            ##     *****************************    START
            trip_id = get_auto_gen_trip_id( str(datetime.utcnow()), app_user.get_email())

            trips_output = [] # set empty str
            admin_result = repo.get_trip_list(app_user.get_email(), True)  # list of admin trip_id(s) in 'user' table
            user_result = repo.get_trip_list(app_user.get_email(), False)  # list of user trip_id(s) in 'user' table
            

            if not admin_result or admin_result[0] == 'None' :
                pass
            else:
                ## 'admin_list' from Database Table 'trips' to table view (html)
                admin_list = []
                for each in admin_result:
                    admin_list.append(repo.get_trips_from_trips_table(each))
                trips_output.append(get_trips_in_table(admin_list, True))
                pass

            if not user_result or user_result[0] == 'None':
                pass
            else:
                ## 'user_list' from Database Table 'trips' to table view (html)
                user_list = []
                for each in user_result:
                    user_list.append(repo.get_trips_from_trips_table(each))
                trips_output.append(get_trips_in_table(user_list, False))
                pass

            trips_output = Markup(" ".join(trips_output))

            return render_template(
            'index.html',
            title='Home Page',
            user_name = app_user.get_fname() ,
            travel_id = travel_id,
            auto_gen_trip_id = trip_id,
            show_trip_list = trips_output,
            year=datetime.now().year
            )
            ##    *****************************    END




        elif request.form['new_trip'] == 'create_new':

            print("[new_trip] = create_new")
            
            # invalid input handling (TO DO)
            trip_name = request.form['new_trip_name']

            t = Trip(trip_id, trip_name, app_user.get_email())
            repo.add_trip_name(t, True)
                       
           
            ##     *****************************    START
            trip_id = get_auto_gen_trip_id( str(datetime.utcnow()), app_user.get_email())

            trips_output = [] # set empty str
            admin_result = repo.get_trip_list(app_user.get_email(), True)  # list of admin trip_id(s) in 'user' table
            user_result = repo.get_trip_list(app_user.get_email(), False)  # list of user trip_id(s) in 'user' table
            

            if not admin_result or admin_result[0] == 'None' :
                pass
            else:
                ## 'admin_list' from Database Table 'trips' to table view (html)
                admin_list = []
                for each in admin_result:
                    admin_list.append(repo.get_trips_from_trips_table(each))
                trips_output.append(get_trips_in_table(admin_list, True))
                pass

            if not user_result or user_result[0] == 'None':
                pass
            else:
                ## 'user_list' from Database Table 'trips' to table view (html)
                user_list = []
                for each in user_result:
                    user_list.append(repo.get_trips_from_trips_table(each))
                trips_output.append(get_trips_in_table(user_list, False))
                pass

            trips_output = Markup(" ".join(trips_output))

            return render_template(
            'index.html',
            title='Home Page',
            user_name = app_user.get_fname() ,
            travel_id = travel_id,
            auto_gen_trip_id = trip_id,
            show_trip_list = trips_output,
            year=datetime.now().year
            )
            ##    *****************************    END 


        
        if( is_bad_str(trip_name) ):
            msg = "WRONG INPUT: please try again to create a trip list"
            return render_template('wrongInputTrip.html',
                                   user_name = app_user.get_fname() ,
                                   msg = msg
                                   )
            

                        


### *********************************************************************************************************************
### #######################################                 TRIP PAGE                 ####################################
### *********************************************************************************************************************
@app.route('/trip/<trip_id>', methods=['GET', 'POST'])
def trip(trip_id):
    if request.method == 'GET': # ------------------------------------------------------------------------------------------------ Get
        output = ""
        travel_result = repo.get_travel_events(trip_id)  # list of tuples
        
        for event in travel_result:
            add = """
                <tr>  
                    <td>              
            """
            output += add
            for cell in event:
                add =  cell + """</td>
                                 <td>"""
                output += add

            add = """</td>
                            </tr>
                        """
            output += add
            
        output = Markup(output)

        return render_template(
        'trip.html',
        title='Home Page',
        user_name = user_name,
        travel_id = travel_id,
        trip_id = trip_id,
        sorted_result = output,
        year=datetime.now().year,
        )
    elif request.method == 'POST':   # ------------------------------------------------------------------------------------------------ POST

        # retrieve lists
        flights = request.values.getlist('flight')
        print(type(flights))
        print(len(flights))
        print(flights)
        
        flights_dt = request.values.getlist('flight_datetime')
        hotels = request.values.getlist('hotel')
        hotels_dt = request.values.getlist('hotel_datetime')
        places = request.values.getlist('place')
        places_dt = request.values.getlist('place_datetime')

        f_obj_list = []
        h_obj_list = []
        p_obj_list = []        

        # save respective objs in lists
        if(len(flights)!= 0 and len(flights)==len(flights_dt)):
            for i in range(len(flights)):

                # input validation 
                if(not is_valid_datetime(flights_dt[i]) or is_bad_str(flights[i]) ):
                    msg = ""
                    if(not is_valid_datetime(flights_dt[i])):
                        msg = msg + "<p style='color:#f00'><b>INVALID INPUT:</b> please try again to create a trip 'Flight Date/Time' field</p>"
                    if(is_bad_str(flights[i])):
                        msg = msg + "<p style='color:#f00'><b>INVALID INPUT:</b> please try again to create a trip 'Flight Name' field</p>"
                    
                    return render_template('wrongInputField.html',
                                           trip_id= trip_id,
                                            user_name = user_name,
                                            msg = Markup(msg)
                                            )
            

                f_obj = Flight(trip_id, flights_dt[i], flights[i] )  # create a Flight obj
                url = 'https://flightaware.com/live/flight/' + str(f_obj.info)
                req = req = requests.get(url)
                soup = BeautifulSoup(req.text, "html.parser")
                flight_state = []  # from website https://flightware.com/live/flight/
                for each in soup.findAll("td", {"class": "smallrow1"}):
                    flight_state.append(each.text)

                
                if(len(flight_state) == 0):
                    f_obj.status="NOT AVAILABLE"
                else:  # flight information is good to go
                    print(flight_state)  # keep going  & show live flight info
                    f_obj.status = str(re.sub(r'\([^)]*\)', '', flight_state[0]))    

                f_obj_list.append(f_obj)

        if(len(hotels)!= 0 and len(hotels)==len(hotels_dt)):


            for i in range(len(hotels)):
                # input validation 
                if(not is_valid_datetime(hotels_dt[i]) or is_bad_str(hotels[i]) ):
                    msg = ""
                    if(not is_valid_datetime(hotels_dt[i])):
                        msg = msg + "<p style='color:#f00'><b>INVALID INPUT:</b> please try again to create a trip 'Hotel Date/Time' field</p>"
                    if(is_bad_str(hotels[i])):
                        msg = msg + "<p style='color:#f00'><b>INVALID INPUT:</b> please try again to create a trip 'Hotel Name' field</p>"
                    
                    return render_template('wrongInputField.html',
                                            trip_id= trip_id,
                                            user_name = user_name,
                                            msg = Markup(msg)
                                            )

                h_obj = Hotel(trip_id, hotels_dt[i], hotels[i] )
                h_obj_list.append(h_obj)

        if(len(places)!= 0 and len(places)==len(places_dt)):

            for i in range(len(places)):
                # input validation 
                if(not is_valid_datetime(places_dt[i]) or is_bad_str(places[i]) ):
                    msg = ""
                    if(not is_valid_datetime(places_dt[i])):
                        msg = msg + "<p style='color:#f00'><b>INVALID INPUT:</b> please try again to create a trip 'Place Date/Time' field</p>"
                    if(is_bad_str(places[i])):
                        msg = msg + "<p style='color:#f00'><b>INVALID INPUT:</b> please try again to create a trip 'Place Name' field</p>"
                    
                    return render_template('wrongInputField.html',
                                            trip_id= trip_id,
                                            user_name = user_name,
                                            msg = Markup(msg)
                                            )

                p_obj = Place(trip_id, places_dt[i], places[i] )
                p_obj_list.append(p_obj)
            
        # add to repo -> database
        for each_flight_obj in f_obj_list:
            repo.add_flight(each_flight_obj)
        for each_hotel_obj in h_obj_list:
            repo.add_hotel(each_hotel_obj)
        for each_place_obj in p_obj_list:
            repo.add_place(each_place_obj)

        # time to display
        output = ""
        travel_result = repo.get_travel_events(trip_id)  # list of tuples        
        for event in travel_result:
            add = """
                <tr>  
                    <td>              
            """
            output += add
            for cell in event:
                add =  cell + """</td>
                                 <td>"""
                output += add

            add = """</td>
                            </tr>
                        """
            output += add
            
        output = Markup(output)

        return render_template('trip.html',
                user_name = user_name,
                travel_id = travel_id,
                trip_id = trip_id,
                sorted_result = output,
                year=datetime.now().year,
                )





### *********************************************************************************************************************
### #######################################                 OTHER FUNCTIONS          ####################################
### ********************************************************************************************************************* 

def is_valid_datetime(d):
    try:
        datetime.strptime(d, '%Y-%m-%dT%H:%M')
        return True
    except ValueError:
        return False

def is_bad_str(string):
    if not string:
        return True
    else:
        return False


def get_auto_gen_trip_id(temp_trip_id, temp_user_id):
    return str(re.sub(r'[\W]+', '', temp_user_id+temp_trip_id))


def get_trips_in_table(trip_list, admin): 
    
    if admin:
        button_color = """btn btn-success btn-sm pull-right"""
        button_text = """Admin View"""
    else:
        button_color = """btn btn-default btn-sm pull-right"""
        button_text = """User View"""
    

    trips_output_text_line = ""
    temp_trip_id = "temp trip id"
    for event in trip_list:
        turn = False
        t_add = """<tr><td>"""
        trips_output_text_line += t_add
        for cell in event:
            if(turn == False):
                temp_trip_id = cell
                turn = True
            t_add = cell + """ </td><td>"""
            trips_output_text_line += t_add
                
        t_add = """<td><button type="button" class=" """ + button_color + """ " onclick="location.href = '/trip/"""
        trips_output_text_line += t_add
        trips_output_text_line += str(temp_trip_id)
                    
        t_add = """';">""" + button_text + """</button></td>
                </td>
                    </tr>
                """
        trips_output_text_line += t_add
    return trips_output_text_line    # string













### ----------------------------------------- OLD ------------------------------------------------------------------------------------------------------------------------------
### ----------------------------------------- OLD ------------------------------------------------------------------------------------------------------------------------------

@app.route('/userInput', methods=['GET', 'POST'])
def userInput():

    if request.method == 'GET':
        return render_template('UserInput.html')

    elif request.method == 'POST':         # ----------------------------------------------------------------------------------------  -------------- post

        flight = Flight(travel_id, request.form['flight_datetime'], request.form['flight'] )  # request.form['flight_datetime']
        hotel = Hotel(travel_id, request.form['hotel_datetime'], request.form['hotel'] )  # request.form['hotel_datetime']
        place  = Place(travel_id, request.form['place_datetime'], request.form['place'] )  # request.form['place_datetime']

        # return incorrect flight info page when result is not available
        # retrieve live flight information from website (no free api I found so far..)
        url = 'https://flightaware.com/live/flight/' + str(flight.info)
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        flight_state = []  # from website https://flightware.com/live/flight/
        for each in soup.findAll("td", {"class": "smallrow1"}):
            flight_state.append(each.text)

        output = """
                <tr>
                    <th>Event</th>
                    <th>Detail</th>
                    <th>Date/Time</th>
                    <th>Status</th>
                </tr>
        """

        if(len(flight_state) == 0):
            flight.status="NOT AVAILABLE"
            tl = [flight, hotel, place]
            tl.sort(key= lambda obj: obj.datetime)            

            for obj in tl:            
                add =  """
                            <tr>
                                <td>""" + obj.title + """</td>
                                <td>""" + obj.info + """</td>
                                <td>""" + obj.datetime + """</td>
                                <td style='color:#f00'>""" + obj.status + """</td>
                            </tr>
                        """
                output += add
            
            output = Markup(output)
            return render_template('IncorrectFlightInfo.html', 
                            travel_id = travel_id, sorted_result= output
                            )
        else:  # flight information is good to go
            print(flight_state)  # keep going  & show live flight info
            flight.status = str(re.sub(r'\([^)]*\)', '', flight_state[0]))


        repo.add_travel_info(flight, hotel, place)

        # return result information when flight info is availalble 
        # dt = datetime.datetime.strptime(flight.datetime, "%Y-%m-%dT%H:%M")  # conversion
        
        tl = [flight, hotel, place]
        tl.sort(key= lambda obj: obj.datetime)
                
        for obj in tl:
            
            add =  """
                        <tr>
                            <td>""" + obj.title + """</td>
                            <td>""" + obj.info + """</td>
                            <td>""" + obj.datetime + """</td>
                            <td style='color:#00bde4'>""" + obj.status + """</td>
                        </tr>
                    """
            output += add
            
        output = Markup(output)
        return render_template('ShowTravelInfo.html', 
                               travel_id = travel_id, sorted_result= output)

    return   # end of userInput()


@app.route('/travel', methods=['GET', 'POST'])
def travel():
    if request.method == 'GET':
        return render_template('ShowTravelInfo.html', travel_id = travel_id)
    elif request.method == 'POST':
        travel_result = repo.get_travel_events(travel_id)  # list of tuples
        output = ""
        for event in travel_result:
            add = """
                <tr>  
                    <td>              
            """
            output += add
            for cell in event:
                add =  cell + """</td>
                                <td>"""
                output += add

            add = """</td>
                            </tr>
                        """
            output += add
            
        output = Markup(output)
        return render_template('ShowTravelInfo.html', 
                               travel_id = travel_id, sorted_result= output)
        # return str(result_flight)

    return



