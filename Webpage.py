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
                if date[0:10] not in dates:
                    dates.append(date[0:10])
                print(date)
        return dates
    
    @cherrypy.expose
    def index(self,weight=60):                   
        template = JINJA_ENVIRONMENT.get_template('Charts.html')
        
        
        dates = self.get_dates()
        
        
        data=[]
        for row in dates:
            time_min, time_max = self.get_times()
            time_min = datetime.strptime(time_min[:7], "%H:%M:%S").time()
            time_max = datetime.strptime(time_max[:7], "%H:%M:%S").time()
            duration_time = datetime.combine(date.today(), time_max) - datetime.combine(date.today(), time_min)
            (h, m, s) = str(duration_time).split(":")
            duration_int = int(h) * 3600 + int(m) * 60 + int(s)
            Cal = (weight * 9) * duration_int
            
            data.append( (row,Cal) )
                #break
        #data =  [("1/12/18",100),
                #("2/12/18",200),
                #("3/12/18",400)]
       # print(data)
        template_values = {
            'data' : data}
        return template.render(template_values)
    #Cal burnt = (weight in kg * activity value) * time doing
    def get_times(self):
        with sql.connect(DB) as cur:
            results = cur.execute( '''SELECT MIN(time), MAX(time) FROM Location GROUP BY date;''')
            for row in results:
                return row
       
    
if __name__ == '__main__':
    w = Website()
    w.index()
    
    cherrypy.config.update( {'server.socket_host': '0.0.0.0'} ) # make it accesible from other machines 
    cherrypy.quickstart( Website() )

