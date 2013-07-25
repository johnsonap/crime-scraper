import os, urllib2, re, simplejson, urlparse
from bs4 import BeautifulSoup
from pymongo import Connection
from flask import Flask
from flask import render_template

app = Flask(__name__)
# provides the do statement for figuring out if suspect exists in suspect json in templates
app.jinja_env.add_extension('jinja2.ext.do')

MONGO_URL = os.environ.get('MONGOHQ_URL')
# check to see if the MONGO_URL exists, otherwise just connect locally
if MONGO_URL:
    connection = Connection(MONGO_URL)
    db = connection[urlparse.urlparse(MONGO_URL).path[1:]]
else:
    connection = Connection('localhost', 27017)
    db = connection['wanted_suspects']

# get the blob from the database it, parse it with simplejson, spit it into a template
@app.route('/')
def index():
    suspect_data = simplejson.loads(db.suspects.find_one({'data':'suspects'})['json'])
    return render_template('index.html',suspects=suspect_data)

# individual suspect pages, some hackery involved in the template because I'm passing in the whole suspect json blob
@app.route('/suspect/<suspect_name>')
def suspect_page(suspect_name=None):
    # need to sanitize name input
    suspect_data = db.suspects.find_one({'data':'suspects'})['json']
    suspects = simplejson.loads(suspect_data)
    return render_template('suspect_page.html',suspects=suspects,suspect_name=suspect_name)
   
# this route provides the raw suspects json blog in plain-text
@app.route('/json')
def json():
    suspect_data = db.suspects.find_one({'data':'suspects'})['json']
    return suspect_data, 200, {'Content-Type': 'text/plain'}
    
# used to update the database, run every Monday morning using the Temporize Scheduler add-on in Heroku
@app.route('/updatelist')
def update():
    page_num_stuff = BeautifulSoup(urllib2.urlopen('http://www.pcstips.com/wanteds.aspx?PageNum=1').read())
    wanted_suspects = []  
    find = page_num_stuff.body.findAll(text = re.compile('Page 1 of'), limit=1)
    pages = find[0].split()
    pagenums = int(pages[len(pages)-1])
    json_str = '{"suspects":[';
    # get all pages of results and store them in the wanted_suspects list
    for page in range(pagenums):
        # prevent a redundant url call since we already grabbed the first page to check the number of pages
        if (page == 0):
            soup = page_num_stuff
        else:
            soup = BeautifulSoup(urllib2.urlopen('http://www.pcstips.com/wanteds.aspx?PageNum=' + str(page+1)).read())
        print page
        #find the stuff for each suspect
        for table in soup.find(id="styles").find_all("table"):
            if( table.attrs == {'width': '100%', 'style': 'table-layout: fixed;bborder-collapse:collapse;', 'border': '1'}):
                for inside_table in table.find_all("table"):
                    if( inside_table.attrs == {'bgcolor': '#eeeeee', 'style': 'border-collapse:collapse', 'border': '1', 'width': '100%'}):
                        # need to sanitize these scrapes
                        demo_table = inside_table.parent.parent.parent.parent.table.next_sibling
                        wanted_date = str(inside_table.parent.parent.parent.tr.td.center).split("</b>")[1].split("</center")[0]
                        img = "http://www.pcstips.com/" + inside_table.parent.parent.parent.parent.find_previous_sibling("td").a.get("href")
                        link = "http://www.pcstips.com/" + inside_table.parent.parent.parent.parent.find_previous_sibling("td").a.find_next_sibling("a").get("href")
                        name = inside_table.tr.td.p.b.string
                        alias = demo_table.find(text=re.compile('Alias')).parent.parent.next_sibling.string.strip()
                        gender = demo_table.find(text=re.compile('Sex')).parent.parent.next_sibling.string.strip()
                        race = demo_table.find(text=re.compile('Race')).parent.parent.next_sibling.string.strip()
                        dob = demo_table.find(text=re.compile('DOB')).parent.parent.next_sibling.string.strip()
                        height = demo_table.find(text=re.compile('Height')).parent.parent.next_sibling.string.strip()
                        weight = demo_table.find(text=re.compile('Weight')).parent.parent.next_sibling.string.strip()
                        hair_color = demo_table.find(text=re.compile('Hair')).parent.parent.next_sibling.string.strip()
                        eye_color = demo_table.find(text=re.compile('Eyes')).parent.parent.next_sibling.string.strip()
                        charges = table.find("font").string
                        json_str += '{"name": "' + str(name) + '", "charges": "' + str(charges) + '", "img": "' +   str(img) + '", "link": "' + str(link) + '", "wanted_date": "' + str(wanted_date) +'", "alias": "'+ str(alias) + '", "gender": "' + str(gender) + '", "race" : "' + str(race) +'", "dob" : "' + str(dob) + '", "height": "' +str(height) +'", "weight": "' + str(weight) + '", "hair_color": "' + str(hair_color) + '", "eye_color": "' + str(eye_color) + '"},'

    # I should probably find a better way to do this than manually writing out the JSON, but it works for now                        
    json_str = json_str[0:len(json_str)-1] + ']}'
    data = db.suspects.find_one({'data':'suspects'})
    if not data:
        data = {'data':'suspects', 'json':json_str}
    else:
        data['json'] = json_str
    db.suspects.save(data)
    return "Done", 200, {'Content-Type' : 'text/plain'}
    
    
    
    