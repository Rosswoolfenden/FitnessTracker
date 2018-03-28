import cherrypy
import sqlite3 as sql
from datetime import datetime, date, time
import math, jinja2, os

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),extensions=['jinja2.ext.autoescape'])

DB = 'location.db'

class Website(object):
    
    @cherrypy.expose
    def index(self):
        template = JINJA_ENVIRONMENT.get_template('home.html')
        template_values = {
            'image' : os.path.join(os.path.dirname(__file__),'images/image1.png')
        }    
        return template.render(template_values)
    
    def get_dates(self):
        dates = []
        with sql.connect(DB) as cur:
            results = cur.execute( '''SELECT date FROM Location;''')
            for date, in results:
                if date not in dates:
                    dates.append(date)
        return dates
    
    def get_times(self):
        with sql.connect(DB) as cur:
            results = cur.execute( '''SELECT MIN(time), MAX(time) FROM Location GROUP BY date;''')
            durations = []
            for row in results:
                time_min, time_max = row
                time_min = datetime.strptime(time_min[:8], "%H:%M:%S").time()
                time_max = datetime.strptime(time_max[:8], "%H:%M:%S").time()
                duration_time = datetime.combine(date.today(), time_max) - datetime.combine(date.today(), time_min)
                (h, m, s) = str(duration_time).split(":")
                duration_int = int(h) + int(m)/60 + int(s)/3600
                durations.append(duration_int)
            return durations
    
    def get_loc(self):
        with sql.connect(DB) as cur:
            results = cur.execute( '''SELECT MIN(longitude), MAX(longitude), MIN(latitude), MAX(latitude) FROM Location Group by date;''')
            distances = []
            for row in results:
                lon_min, lon_max, lat_min, lat_max = row
                dlon = lon_max - lon_min
                dlat = lat_max - lat_min
                a = (math.sin(dlat/2))**2 + math.cos(lat_min) * math.cos(lat_max) * (math.sin(dlon/2))**2
                c = 2 * math.atan2( math.sqrt(a), math.sqrt(1-a) )
                d = 3959 * c #radius of earth in miles
                distances.append(str(d)[:5])
        return distances
        
    @cherrypy.expose
    def recent_runs(self,weight=1):                   
        template = JINJA_ENVIRONMENT.get_template('recent_runs.html')
        
        dates = self.get_dates()
        durations = self.get_times()
        distances = self.get_loc()
        cal_data=[]
        dist_data=[]
        for e in range(len(dates)):
            Cal = (int(weight) * 8) * durations[e] #Cal burnt = (weight in kg * metabolic activity value) * time doing(hours)
            cal_data.append( (dates[e],Cal) )
        for i in range(len(dates)):
            dist_data.append( (dates[i], distances[i]) )
        #print(cal_data)
        print(dist_data)
        template_values = {
            'cal_data' : cal_data,
            'dist_data' : dist_data
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
            'tools.staticdir.dir': 'images'
        }
    }
    cherrypy.config.update( {'server.socket_host': '0.0.0.0'} ) # make it accesible from other machines 
    cherrypy.quickstart(Website(), '/', conf)

