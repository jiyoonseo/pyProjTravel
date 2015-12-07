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
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_user' in session:
            return f(*args, **kwargs)
        else:
            flash("A login is required to see the page!")
            return redirect(url_for('login', next=request.path))
    return decorated_function



#login_logout = "Log In" # global login_logout

# travel_id = "ok whatever"
# user_id = "user_js_01"
# user_name = "happy tree"

@app.route('/')  # temp --> remove later
@app.route('/logout')
def logout():
    session.pop('session_user', None)
    session.pop('logged_in', None)
    session['log'] = False
    return redirect(url_for('login'))  



### *********************************************************************************************************************
### #######################################                 ROOT PAGE                 ####################################
### *********************************************************************************************************************
# @app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods =['GET','POST'])
def login():
    
    if request.method == 'GET' and session.get('session_user') is None :
        
        return render_template('login.html', 
                               acc = "'s Account" if session['log'] else "",
                               log_in_out = 'Log Out' if session['log'] else 'Log In')

    elif request.method == 'POST':
        if request.form['auth'] == 'login':
            user_email = request.form['login_email']
            user_pw = request.form['login_pw']

            ### after having useremail && password 
            login_user = repo.get_user_obj(user_email)
            if not login_user :
                flash("Username is not found in database. Please create an account.")
                return redirect(url_for('login'))                
                
            else: # when user account is found
                print("login_user FOUND")
                if login_user.check_password(user_pw):
                    session['session_user'] = user_email
                    session['logged_in'] = True
                    session['log'] = True
                                        
                    app_user.reset_all(login_user.email, login_user.pw_hash, login_user.fname, login_user.lname)
                    return redirect(url_for('home'))  

                else:  # inaccurate password
                    flash("Username/Password was incorrect")
                    return redirect(url_for('login')) 
                pass
        elif request.form['auth'] == 'create_account':
            
            print('create_account--- form has been sent')

            email = pw = fname = lname = None

            # required forms.. form validation
            
            if request.form['create_login_email'] :
                email = request.form['create_login_email'] 
                if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
                    pass
                else:
                    email = None
                    flash("Email is invalid.")
                pass
            else:
                flash("Email is required to create an account. Please try again.")
                pass

            if request.form['create_login_pw'] and request.form['create_login_pw'] == request.form['confirm_login_pw']:
                pw = request.form['create_login_pw']   
                pass
            elif not request.form['create_login_pw'] or not request.form['confirm_login_pw']:
                flash("Password and Password Confirmation is required to create an account. Please try again.")
                pass
            elif request.form['create_login_pw'] != request.form['confirm_login_pw']:
                flash("Password and Password Confirmation should be matched to create an account. Please try again.")
                pass

            if request.form['create_account_fname'] :
                fname = request.form['create_account_fname']
                pass
            else:
                flash("First Name is required to create an account. Please try again.")
                pass

            if request.form['create_account_lname'] :
                lname = request.form['create_account_lname']
                pass
            else:
                flash("Last Name is required to create an account. Please try again.")
                pass


            successful_create = False
            if email and pw and fname and lname:
                temp_user = User(email, pw, fname, lname, 0)
                repo.create_user(temp_user)    
                successful_create = True    

            
            return render_template('login.html', message=Markup("<div style='color:#f0f;'>Thank you for create an account! </div>") if successful_create else Markup("<div style='color:#f00;'>Failed to create an account. </div>"),
                                   acc = "'s Account" if session['log'] else "",
                                   log_in_out = 'Log Out' if session['log'] else 'Log In')
            pass

     



### *********************************************************************************************************************
### #######################################            user ACCOUNT PAGE              ####################################
### *********************************************************************************************************************
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    global login_logout
    if request.method == 'GET':

        
        return render_template('account.html', 
                               user_name = app_user.fname, 
                               user_lname = app_user.lname , 
                               user_email = app_user.get_email(),
                               acc = "'s Account" if session['log'] else "",
                               log_in_out = 'Log Out' if session['log'] else 'Log In',
                               year=datetime.now().year)
        
    elif request.method == 'POST':

        ### TO DO 's
        ### @1 after validation, 
        ### @2 update table with new user_obj
        ### @3 set user_obj with newly retrieved information (together with @2)

        flash_list = []
        update_success = False
        # only password is required in this page...
        if request.form['login_pw']:
            
            old_username = app_user.email # temp save in case user change his/her username
            # validate password
            if app_user.check_password(request.form['login_pw']):               
                
                """
                if request.form['account_email']:
                    app_user.email = request.form['account_email']
                    session['session_user'] = app_user.email
                """
                update_success = True

                # not required..
                if request.form['account_fname']:
                    app_user.fname = request.form['account_fname']
                
                # not required..
                if request.form['account_lname']:
                    app_user.lname = request.form['account_lname']
                
                # not required..
                if request.form['create_new_pw'] and request.form['confirm_new_pw']:
                    if request.form['create_new_pw'] == request.form['confirm_new_pw']:
                        app_user.set_password(request.form['create_new_pw'])                    
                    else:
                        flash("New Password and Password Confirmation is not matched.")
                        update_success = False
                        
                if not update_success:
                    flash("Your information has not been saved!")
                else:
                    repo.update_user(app_user, old_username)
                    flash("Updated Successfully!")

                pass
            else:
                flash("Current Password is not correct. Please try again.")
                pass
        
        else:
            flash("You MUST provide your current password to securely update your information.")
            pass

        

        return render_template('account.html', 
                               user_name = app_user.fname, 
                               user_lname = app_user.lname , 
                               user_email = app_user.get_email(),
                               acc = "'s Account" if session['log'] else "",
                               log_in_out = 'Log Out' if session['log'] else 'Log In',
                               year=datetime.now().year)
        

    pass



        

### *********************************************************************************************************************
### #######################################                 HOME PAGE                 ####################################
### *********************************************************************************************************************
trip_id = ""  # need it as global for auto-gen key
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    #global login_logout
    global trip_id
    if request.method == 'GET': 

        if session.get('logged_in') and session['logged_in'] == True :
            trip_id = get_auto_gen_trip_id( str(datetime.now()), app_user.get_email())

            trips_output = [] # set empty str
            admin_result = repo.get_trip_list(app_user.get_email(), True)  # list of admin trip_id(s) in 'user' table
            user_result = repo.get_trip_list(app_user.get_email(), False)  # list of user trip_id(s) in 'user' table
            
            all_users = []
            sorted_by_datetime_all = []
            if not admin_result or admin_result[0] == 'None' :
                pass
            else:
                ## 'admin_list' from Database Table 'trips' to table view (html)
                admin_list = []
                for each in admin_result:
                    admin_list.append(repo.get_trips_from_trips_table(each))                    
                #1. trips_output.append(get_trips_in_table(admin_list, True))
                all_users.extend(admin_list)
                
                pass

            if not user_result or user_result[0] == 'None':
                pass
            else:
                ## 'user_list' from Database Table 'trips' to table view (html)
                user_list = []
                for each in user_result:
                    user_list.append(repo.get_trips_from_trips_table(each))
                #2. trips_output.append(get_trips_in_table(user_list, False))
                all_users.extend(user_list)
                
                pass

            
            #3. trips_output = Markup(get_trips_in_table(sorted_by_datetime_all))
            # sort by datetime
            if all_users:
                sorted_by_datetime_all = sorted(all_users, key=lambda tup: tup[3])
                trips_output = Markup(get_trips_in_table(sorted_by_datetime_all))
            else:
                trips_output = "Create or Add your First Trip!"
                
            
            ### END..........................................

            #trips_output = Markup(" ".join(trips_output))

            return render_template(
            'index.html',
            title='Home Page',
            user_name = app_user.get_fname() ,
            auto_gen_trip_id = trip_id,
            acc = "'s Account" if session['log'] else "",
            log_in_out = 'Log Out' if session['log'] else 'Log In',
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
                        
            # invalid input handling 
            existing_trip_id = ""
            if request.form['existing_trip_id']:
                existing_trip_id = request.form['existing_trip_id'] 
                current_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M')
                t = Trip(existing_trip_id, 'trip_name', app_user.get_email(), current_datetime, current_datetime)  # trip_id, trip_name, user_id(email)

                # check if the trip_id is existing ? (True or False)
                # repo.check_exist_trip(existing_trip_id) # True or False
                if repo.check_exist_trip(existing_trip_id):
                    repo.add_trip_name(t, False)
                else:
                    flash_line = "The Trip Id '" + existing_trip_id + "' is not found. Please try again." 
                    flash(flash_line)
                pass
            else:
                flash("Please Enter Existing Trip Id")
                pass

            

            ##     *****************************    START
            

            trips_output = [] # set empty str
            admin_result = repo.get_trip_list(app_user.get_email(), True)  # list of admin trip_id(s) in 'user' table
            user_result = repo.get_trip_list(app_user.get_email(), False)  # list of user trip_id(s) in 'user' table
            
            all_users = []
            sorted_by_datetime_all = []
            if not admin_result or admin_result[0] == 'None' :
                pass
            else:
                ## 'admin_list' from Database Table 'trips' to table view (html)
                admin_list = []
                for each in admin_result:
                    admin_list.append(repo.get_trips_from_trips_table(each))
                #1. trips_output.append(get_trips_in_table(admin_list, True))
                all_users.extend(admin_list)
                pass

            if not user_result or user_result[0] == 'None':
                pass
            else:
                ## 'user_list' from Database Table 'trips' to table view (html)
                user_list = []
                for each in user_result:
                    user_list.append(repo.get_trips_from_trips_table(each))
                #2. trips_output.append(get_trips_in_table(user_list, False))
                all_users.extend(user_list)
                pass

            #3. trips_output = Markup(" ".join(trips_output))
            # sort by datetime
            if all_users:
                sorted_by_datetime_all = sorted(all_users, key=lambda tup: tup[3])
                trips_output = Markup(get_trips_in_table(sorted_by_datetime_all))
            else:
                trips_output = "Create or Add your First Trip!"
                

            return render_template(
            'index.html',
            title='Home Page',
            user_name = app_user.get_fname() ,
            # travel_id = travel_id,
            auto_gen_trip_id = trip_id,
            show_trip_list = trips_output,
            acc = "'s Account" if session['log'] else "",
            log_in_out = 'Log Out' if session['log'] else 'Log In',
            year=datetime.now().year
            )
            ##    *****************************    END




        elif request.form['new_trip'] == 'create_new':
                        
            # invalid input handling (TO DO)
            trip_name = ""

            if request.form['new_trip_name']:
                trip_name = request.form['new_trip_name']
                current_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M')
                t = Trip(trip_id, trip_name, app_user.get_email(), current_datetime, current_datetime)
                repo.add_trip_name(t, True)
            else:
                flash("Please Enter Trip Name.")
            
           
            ##     *****************************    START
            trip_id = get_auto_gen_trip_id( str(datetime.now()), app_user.get_email())

            trips_output = [] # set empty str
            admin_result = repo.get_trip_list(app_user.get_email(), True)  # list of admin trip_id(s) in 'user' table
            user_result = repo.get_trip_list(app_user.get_email(), False)  # list of user trip_id(s) in 'user' table
            
            all_users = []
            sorted_by_datetime_all = []
            if not admin_result or admin_result[0] == 'None' :
                pass
            else:
                ## 'admin_list' from Database Table 'trips' to table view (html)
                admin_list = []
                for each in admin_result:
                    admin_list.append(repo.get_trips_from_trips_table(each))
                #1. trips_output.append(get_trips_in_table(admin_list, True))
                all_users.extend(admin_list)
                pass

            if not user_result or user_result[0] == 'None':
                pass
            else:
                ## 'user_list' from Database Table 'trips' to table view (html)
                user_list = []
                for each in user_result:
                    user_list.append(repo.get_trips_from_trips_table(each))
                #2. trips_output.append(get_trips_in_table(user_list, False))
                all_users.extend(user_list)
                pass

            #3. trips_output = Markup(" ".join(trips_output))
            # sort by datetime
            if all_users:
                sorted_by_datetime_all = sorted(all_users, key=lambda tup: tup[3])
                trips_output = Markup(get_trips_in_table(sorted_by_datetime_all))
            else:
                trips_output = "Create or Add your First Trip!"

            return render_template(
            'index.html',
            title='Home Page',
            user_name = app_user.get_fname() ,
            # travel_id = travel_id,
            auto_gen_trip_id = trip_id,
            show_trip_list = trips_output,
            acc = "'s Account" if session['log'] else "",
            log_in_out = 'Log Out' if session['log'] else 'Log In',
            year=datetime.now().year
            )
            ##    *****************************    END 


        
        if( is_bad_str(trip_name) ):
            msg = "WRONG INPUT: please try again to create a trip list"
            return render_template('wrongInputTrip.html',
                                   user_name = app_user.get_fname() ,
                                   msg = msg
                                   )
            

                        
def get_trip_events_in_table(trip_id):
    global login_logout
    output = ""
    travel_result = repo.get_travel_events(trip_id)  # list of tuples

    # sort by datetime
    sorted_by_datetime = sorted(travel_result, key=lambda tup: tup[2])
            
    # display trip events in trip obj
    for event in sorted_by_datetime:
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
        
    return output

### *********************************************************************************************************************
### #######################################                 TRIP PAGE                 ####################################
### *********************************************************************************************************************
@app.route('/trip/<trip_id>', methods=['GET', 'POST'])
@login_required
def trip(trip_id):
    if request.method == 'GET': # ------------------------------------------------------------------------------------------------ Get

        output = get_trip_events_in_table(trip_id)
        output = Markup(output)

        # get admin_user_id
        admin_user_of_this_trip = repo.get_admin_user_id(trip_id)

        admin_button = get_admin_button(trip_id, admin_user_of_this_trip)       # admin_button = Markup(admin_button),  

        return render_template(
        'trip.html',
        title='Home Page',
        user_name = app_user.get_fname(),
        trip_id = trip_id,
        trip_name = repo.get_trip_name(trip_id),
        admin_button = Markup(admin_button),
        sorted_result = output,
        acc = "'s Account" if session['log'] else "",
        log_in_out = 'Log Out' if session['log'] else 'Log In',
        year=datetime.now().year,
        )
    elif request.method == 'POST':   # ------------------------------------------------------------------------------------------------ POST

        # retrieve lists

        flights = request.values.getlist('flight')        
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
                                            user_name = app_user.fname,
                                            acc = "'s Account" if session['log'] else "",
                                            log_in_out = 'Log Out' if session['log'] else 'Log In',
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
                                            user_name = app_user.fname,
                                            acc = "'s Account" if session['log'] else "",
                                            log_in_out = 'Log Out' if session['log'] else 'Log In',
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
                                            user_name = app_user.fname,
                                            acc = "'s Account" if session['log'] else "",
                                            log_in_out = 'Log Out' if session['log'] else 'Log In',
                                            msg = Markup(msg)
                                            )

                p_obj = Place(trip_id, places_dt[i], places[i] )
                p_obj_list.append(p_obj)
            
        # add to repo -> database
        for each_flight_obj in f_obj_list:
            repo.add_flight(each_flight_obj)
            # update datetime start/end
            if repo.get_trip_datetime_start(each_flight_obj) > each_flight_obj.datetime:
                repo.update_trip_datetime_start(each_flight_obj.datetime, each_flight_obj.travel_id)
            if repo.get_trip_datetime_end(each_flight_obj) < each_flight_obj.datetime:
                repo.update_trip_datetime_end(each_flight_obj.datetime, each_flight_obj.travel_id)
                
        for each_hotel_obj in h_obj_list:
            repo.add_hotel(each_hotel_obj)
            # update datetime start/end
            if repo.get_trip_datetime_start(each_hotel_obj) > each_hotel_obj.datetime:
                repo.update_trip_datetime_start(each_hotel_obj.datetime, each_hotel_obj.travel_id)
            if repo.get_trip_datetime_end(each_hotel_obj) < each_hotel_obj.datetime:
                repo.update_trip_datetime_end(each_hotel_obj.datetime, each_hotel_obj.travel_id)

        for each_place_obj in p_obj_list:
            repo.add_place(each_place_obj)
            # update datetime start/end
            if repo.get_trip_datetime_start(each_place_obj) > each_place_obj.datetime:
                repo.update_trip_datetime_start(each_place_obj.datetime, each_place_obj.travel_id)
            if repo.get_trip_datetime_end(each_place_obj) < each_place_obj.datetime:
                repo.update_trip_datetime_end(each_place_obj.datetime, each_place_obj.travel_id)
            

        # time to display
        output = ""
        travel_result = repo.get_travel_events(trip_id)  # list of tuples     
        
        # sort by datetime
        sorted_by_datetime = sorted(travel_result, key=lambda tup: tup[2])
        
           
        for event in sorted_by_datetime:
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

        # get admin_user_id
        admin_user_of_this_trip = repo.get_admin_user_id(trip_id)
        
        admin_button = get_admin_button(trip_id, admin_user_of_this_trip)       # admin_button = Markup(admin_button),

        return render_template('trip.html',
                user_name = app_user.get_fname(),
                # travel_id = travel_id,
                trip_id = trip_id,
                trip_name = repo.get_trip_name(trip_id),
                admin_button = Markup(admin_button),
                sorted_result = output,
                acc = "'s Account" if session['log'] else "",
                log_in_out = 'Log Out' if session['log'] else 'Log In',
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


def get_admin_button(trip_id, admin_user_of_this_trip):
    admin_button = None
    if admin_user_of_this_trip == app_user.get_email():
        print("this is admin user")
        admin_button = """
        <button type="button" class="btn btn-danger btn-sm pull-right" data-toggle="modal" data-target="#myModal">
            <span class="glyphicon glyphicon-plus"></span>&nbsp;&nbsp;&nbsp;&nbsp; Add New Field
        </button>
        """
        pass
    else:
        print("this is NOT admin user")
        admin_button = """
        <button type="button" class="btn btn-danger btn-sm pull-right" data-toggle="modal" data-target="#myModal" disabled>
            <span class="glyphicon glyphicon-remove"></span>&nbsp;&nbsp;&nbsp;&nbsp; No Permission to Edit
        </button>
        """
        pass
    return admin_button


def get_trips_in_table(trip_list): 
    
    trips_output_text_line = ""
    temp_trip_id = "temp trip id"
    for event in trip_list:
        turn = False
        t_add = """<tr><td>"""
        trips_output_text_line += t_add
        if event[2] and event[2] == app_user.email:
            button_color = """btn btn-danger btn-sm pull-right"""
            button_text = """Admin View"""
        else:
            button_color = """btn btn-success btn-sm pull-right"""
            button_text = """&nbsp;User &nbspView&nbsp;"""

        for cell in event:
            if cell is None or cell == '' :
                continue
            if(turn == False):
                temp_trip_id = cell
                turn = True
                continue
            t_add = cell + """ </td><td>"""
            trips_output_text_line += t_add

        t_add = """<button type="button" class=" """ + button_color + """ " onclick="location.href = '/trip/"""
        trips_output_text_line += t_add
        trips_output_text_line += str(temp_trip_id)
                    
        t_add = """';">""" + button_text + """</button></td>
                </td>
                    </tr>
                """
        trips_output_text_line += t_add
        pass


    return trips_output_text_line    # string








