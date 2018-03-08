import cherrypy
import sqlite3 as sql
import datetime

import jinja2, os
JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),extensions=['jinja2.ext.autoescape'])

DB = 'location.db'

class Website(object):
	
    def get_dates(self):
        dates = []
        with sql.connect(DB) as cur:
            results = cur.execute( '''SELECT time FROM location.db''')
            for i in range(results.length):
                if results[i[0:10]] != results[i+1[0:10]]:
                    dates.append(results[i[0:10]])
        return dates
    
    @cherrypy.expose
    def index(self):                   
        template = JINJA_ENVIRONMENT.get_template('Charts.html')
        template_values = {
            'dates' : self.get_dates()}
        return template.render(template_values)

if __name__ == '__main__':
    cherrypy.config.update( {'server.socket_host': '0.0.0.0'} ) # make it accesible from other machines 
    cherrypy.quickstart( Website() )
