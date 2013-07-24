import os, urllib2, re, simplejson, urlparse
from bs4 import BeautifulSoup
from flask import Flask
from pymongo import Connection

app = Flask(__name__)
 
MONGO_URL = os.environ.get('MONGOHQ_URL')
 
if MONGO_URL:
    connection = Connection(MONGO_URL)
    db = connection[urlparse.urlparse(MONGO_URL).path[1:]]
else:
    connection = Connection('localhost', 27017)
    db = connection['wanted_suspects']
 

@app.route('/')
def index():
    suspect_data = db.suspects.find_one({'data':'suspects'})['json']
    suspects = simplejson.loads(suspect_data)
    st = "<ul>"
    for suspect in suspects['suspects']:
        st += '<li><img src="' +suspect['img'] + '">' + suspect['name'] + '</li>'
    return st + '</ul>'
    
@app.route('/json')
def json():
    fo = open("foo.txt", "r+")
    return fo.read(), 200, {'Content-Type': 'text/plain'}
    
@app.route('/updatelist')
def update():
    soup = BeautifulSoup(urllib2.urlopen('http://www.pcstips.com/wanteds.aspx?PageNum=1').read())

    wanted_suspects = []
    
    find = soup.body.findAll(text = re.compile('Page 1 of'), limit=1)
    pages = find[0].split()
    pagenums = int(pages[len(pages)-1])
    json_str = '{"suspects":[';
    # get all pages of results and store them in the wanted_suspects list
    for page in range(pagenums):
        soup = BeautifulSoup(urllib2.urlopen('http://www.pcstips.com/wanteds.aspx?PageNum=' + str(page+1)).read())
        print page
        #find the stuff for each suspect
        for table in soup.find(id="styles").find_all("table"):
            if( table.attrs == {'width': '100%', 'style': 'table-layout: fixed;bborder-collapse:collapse;', 'border': '1'}):
                for inside_table in table.find_all("table"):
                    if( inside_table.attrs == {'bgcolor': '#eeeeee', 'style': 'border-collapse:collapse', 'border': '1', 'width': '100%'}):
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
                        json_str += '{"name": "' + str(name) + '", "img": "' +   str(img) + '", "link": "' + str(link) + '", "wanted_date": "' + str(wanted_date) +'", "alias": "'+ str(alias) + '", "gender": "' + str(gender) + '", "race" : "' + str(race) +'", "dob" : "' + str(dob) + '", "height": "' +str(height) +'", "weight": "' + str(weight) + '", "hair_color": "' + str(hair_color) + '", "eye_color": "' + str(eye_color) + '"},'
    json_str = json_str[0:len(json_str)-1] + ']}'
    data = db.suspects.find_one({'data':'suspects'})
    if not data:
        data = {'data':'suspects', 'json':json_str}
    else:
        data['json'] = json_str
    db.suspects.save(data)
    # f = open("foo.txt", "wb")
#     f.write(json_str);
#     
#     # Close opend file
#     f.close()
#     
#     
#     fo = open("foo.txt", "r+")
#     js = simplejson.loads(fo.read())
#     print js['suspects'][0]['name']
#     
#     fo.close()
    return "Done."