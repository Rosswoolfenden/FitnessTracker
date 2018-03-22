import cherrypy
import sqlite3 as sql
from datetime import datetime, date, time

import jinja2, os
JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),extensions=['jinja2.ext.autoescape'])

DB = 'location.db'

class Website(object):
	
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
                print(row)
                time_min, time_max = row
                time_min = datetime.strptime(time_min[:8], "%H:%M:%S").time()
                time_max = datetime.strptime(time_max[:8], "%H:%M:%S").time()
                duration_time = datetime.combine(date.today(), time_max) - datetime.combine(date.today(), time_min)
                (h, m, s) = str(duration_time).split(":")
                duration_int = int(h) * 3600 + int(m) * 60 + int(s)
                durations.append(duration_int)
            return durations
    
    @cherrypy.expose
    def index(self,weight=60):                   
        template = JINJA_ENVIRONMENT.get_template('Charts.html')
        
        dates = self.get_dates()
        durations = self.get_times()
        data=[]
        print(len(dates))
        for e in range(len(durations)):
            Cal = (weight * 9) * durations[e]
            print(Cal)
            data.append( (dates[e],Cal) )
        template_values = {
            'data' : data}
        return template.render(template_values)
    #Cal burnt = (weight in kg * activity value) * time doing
    
    
       
    
if __name__ == '__main__':
    w = Website()
    w.index()
    
    cherrypy.config.update( {'server.socket_host': '0.0.0.0'} ) # make it accesible from other machines 
    cherrypy.quickstart( Website() )

