import math, os
try:
    import cherrypy
except:
    os.system('sudo pip3 install cherrypy')  #if module not present, install it and try again
    os.system('python3 Webpage.py')
try:
    import jinja2
except:
    os.system('sudo pip3 install markupsafe')  #another module that jinja2 depends on
    os.system('sudo pip3 install jinja2')
    os.system('python3 Webpage.py')
import sqlite3 as sql
from datetime import datetime, date, time

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),extensions=['jinja2.ext.autoescape'])

DB = 'location.db'   #name and location of the database

class Website(object):
    
    """the home page"""
    @cherrypy.expose
    def index(self):
        template = JINJA_ENVIRONMENT.get_template('home.html')
        
        return template.render() #finds the template and renders it as a seperate page
    
    """returns a list of dates to display on graphs"""
    def get_dates(self):
        dates = []
        with sql.connect(DB) as cur:
            results = cur.execute('''SELECT DISTINCT date FROM Location;''') #executes a query and fetches all rows of date column
            for date, in results:
                dates.append(date)
        return dates
    
    """returns a list of run durations to calculate calories burned"""
    def get_times(self):
        with sql.connect(DB) as cur:
            results = cur.execute('''SELECT MIN(time), MAX(time) FROM Location GROUP BY date;''')   #for each date, returns the first and the last chronological entry
            durations = []
            for row in results:
                time_min, time_max = row
                time_min = datetime.strptime(time_min[:8], "%H:%M:%S").time()
                time_max = datetime.strptime(time_max[:8], "%H:%M:%S").time()  #for each row, converts the min and max values back from string to a time format
                duration_time = datetime.combine(date.today(), time_max) - datetime.combine(date.today(), time_min)  #formats the values so they can be subractad from each other and then does the math
                (h, m, s) = str(duration_time).split(":")
                duration_int = int(h) + int(m)/60 + int(s)/3600 #splits the result so that it can be converted to hours
                durations.append(duration_int)
            return durations
    
    """converts to radians for calculating geographical distance"""
    def deg2rad(self, deg):
        return deg * (math.pi/180)
    
    def get_loc(self):
        with sql.connect(DB) as cur:
            dates = self.get_dates()
            distances = []
            for i in range(len(dates)):
                locations = [] #stores the coordinates for one day at a time
                results = cur.execute("""SELECT longitude, latitude FROM Location WHERE date = '%s';""" % (dates[i]))
                for row in results:
                    locations.append(row)
                distance = 0
                for i in range(len(locations)-1):
                    lon_1, lat_1 = locations[i]
                    lon_2, lat_2 = locations[i+1]
                    R = 6371 #mean radius of earth in km
                    dlon = self.deg2rad(lon_2 - lon_1)
                    dlat = self.deg2rad(lat_2 - lat_1)
                    a = (math.sin(dlat/2))**2 + math.cos(self.deg2rad(lat_1)) * math.cos(self.deg2rad(lat_2)) * (math.sin(dlon/2))**2
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    d = (R * c) * 0.621371 #calculates the distance and converts it into miles 
                    distance = distance + d #creates a cumulative value for the distance on a certain day
                distances.append(distance)
        return distances   
   
    @cherrypy.expose
    def recent_runs(self,weight=0): #takes weight as a variable for calculating calories burned                  
        template = JINJA_ENVIRONMENT.get_template('recent_runs.html')
        
        dates = self.get_dates()
        durations = self.get_times()
        distances = self.get_loc()
        cal_data=[]
        dist_data=[]
        for e in range(len(dates)):
            Cal = (int(weight) * 8) * durations[e] #Cal burnt = (weight in kg * metabolic activity value) * time doing(hours)
            cal_data.append( (dates[e],Cal) ) #creates the info to be displayed on the calories burned graph
        for i in range(len(dates)):
            dist_data.append( (dates[i], distances[i]) ) #creates the info for the distance covered graph
        template_values = {
            'cal_data' : cal_data,
            'dist_data' : dist_data #inserts the data into the variable slots in the html template
        }
        return template.render(template_values) 
    
    @cherrypy.expose
    def about(self):
        template = JINJA_ENVIRONMENT.get_template('about.html')
        
        return template.render()
       
    
if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'images'             #makes the home page html file properly path to the image files
        }
    }
    cherrypy.config.update( {'server.socket_host': '0.0.0.0'} ) # make it accesible from other machines 
    cherrypy.quickstart(Website(), '/', conf)  #starts hosting the website

    
