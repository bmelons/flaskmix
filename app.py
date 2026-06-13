from flask import Flask, render_template, request, make_response, redirect
import sqlite3
import os
import json
import dotenv
from confighelper import MapObject
from functools import wraps
from werkzeug.utils import secure_filename



app = Flask(__name__)
# set static folder
app._static_folder = 'static'
dotenv.load_dotenv()

 

# CONFIG = None
with open("config.json",'r') as file:
    data = file.read()
    # print(type(data))
    app.config.serverConfig = json.loads(data)
# print(CONFIG["preferences"])

## constants
print(app.config.serverConfig)
SITE_TITLE = app.config.serverConfig["main"]["siteTitle"]

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
def get_connection():
    conn = sqlite3.connect('comic.db')
    conn.row_factory = dict_factory
    return conn
def alternate_connection(x):
    conn = sqlite3.connect(x)
    conn.row_factory = dict_factory
    return conn
def get_character_directory():
    return open('characters.json','r+')
conn = get_connection()



@app.context_processor
def inject_config():
    return dict(
        site_config = app.config.serverConfig
    )

# index
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/readcfg')
def readcfg():
    return render_template('debug/readcfg.html')

@app.route('/chapters')
def chapters():
    # get list of chapters from comic db
    chapters = get_connection().execute('SELECT * FROM chapters').fetchall()

    # get number of highest issue
    return render_template('chapters.html',chapters=chapters)

@app.route('/comic')
def comic():
    return redirect('/comic/1')

@app.route('/socialmedia')
def socialmedia():
    return render_template('socialmedia.html')

@app.route('/comic/last')
def comic_last():
    highest_issue = get_connection().execute('SELECT COUNT(*) FROM comics').fetchone().get('COUNT(*)')
    return redirect('/comic/'+str(highest_issue))

@app.route('/comic/first')
def comic_first():
    return redirect('/comic/1')

@app.route('/comic/<int:issue>')
def comic_issue(issue):
    highest_issue = get_connection().execute('SELECT COUNT(*) FROM comics').fetchone().get('COUNT(*)')
    if issue > highest_issue:
        return page_not_found(404)
    # render comic template if issue is in database
    comic = get_connection().execute('SELECT * FROM comics WHERE rowid=?', (issue,)).fetchone()
    # return str(comic)
    # get number of highest issue
    image_path = comic.get('image_path') or 'placeholder.png'
    row_id = comic.get('rowid') or 0
    desc = comic.get('description') or "..."
    print(highest_issue)
    return render_template('comic.html',d=desc,p=image_path,issue=issue,high=highest_issue)
@app.route('/comic/<int:issue>/')
def comic_issue_slash(issue):
    return redirect('/comic/'+str(issue))

@app.route('/sidecontent')
def side():
    chapters=[]
    # get every json file in ./side-content-data
    for filename in os.listdir('./side-content-data'):
        if filename.endswith('.json'):
            with open('./side-content-data/'+filename) as json_file:
                data = json.load(json_file)
                data["filename"] = filename[:-5]
                chapters.append(data)
                print(data)
    return render_template('sidecontent.html',chapters=chapters)


#region admin
def admin_auth(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
            return make_response("Unauthorized",404)
        
        return f(*args, **kwargs)
    return wrapper

@app.route('/admin',methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        print(request.form.get('username'))
        if request.form.get('username') != os.getenv('COMIC_ADMIN_UNAME'):
            return render_template('admin.html',message='Incorrect.')
        if request.form.get('password') != os.getenv('COMIC_ADMIN_PW'):
            return render_template('admin.html',message='Incorrect.')
        
        resp = make_response(redirect('/adminpanel'))
        resp.set_cookie('user', os.getenv('COMIC_ADMIN_COOKIE'))
        return resp
    return render_template('admin.html')

@app.route('/adminpanel',methods=['GET','POST'])
@admin_auth
def adminpanel():
    # check if cookie is right

    # get comics from database
    
    comics = get_connection().execute('SELECT * FROM comics').fetchall()
    chapters = get_connection().execute('SELECT * FROM chapters').fetchall()
    return render_template('adminpanel.html',comics=comics,chapters=chapters)

@app.route('/adminpanel/add',methods=['POST'])
@admin_auth
def AddComic():
    # get image path and description from form
    image_path = request.form.get('image_path')
    description = request.form.get('description') or "..."
    print(image_path + description)
    # insert into database
    conn = get_connection()
    conn.execute('INSERT INTO comics VALUES (NULL, ?, ?)', (image_path, description))
    conn.commit()
    print("comic added")
    return redirect('/adminpanel')

@app.route('/adminpanel/massadd',methods=['POST'])
@admin_auth
def MassAddComic():

    low = int(request.form.get('low'));
    high = int(request.form.get('high'));
    highest_issue = get_connection().execute('SELECT COUNT(*) FROM comics').fetchone().get('COUNT(*)')
    conn = get_connection()
    for i in range(low,high+1):
        image_path = str(i) + ".png"
        description = " "
        conn.execute('INSERT INTO comics VALUES (NULL, ?, ?, ?, ?)', (image_path, description,"[]",0))
    conn.commit()
    print("comics added")
    return redirect('/adminpanel')
#region
@app.route('/adminpanel/edit',methods=['POST'])
@admin_auth
def EditComic():
    print("edit comic")
    # get id, image path, and description from form
    id = request.form.get('id')
    image_path = request.form.get('image_path')
    description = request.form.get('description') or "..."
    # update database
    conn = get_connection()
    conn.execute('UPDATE comics SET image_path=?, description=? WHERE rowid=?', (image_path, description, id))
    conn.commit()
    print("comic edited")
    return redirect('/adminpanel')

@app.route('/adminpanel/upload',methods=['POST'])
@admin_auth
def UploadToStatic():
    # get image from form
    uploaded_files = request.files.getlist("file")
    print(uploaded_files)
    # save image to static folder
    for image in uploaded_files:
        print(image.filename)
        image.save('static/comic-pages/'+image.filename)
    return redirect('/adminpanel')
@app.route('/adminpanel/uploadchaptericon',methods=['POST'])
@admin_auth
def UploadChapterIcon():
    # get image from form
    uploaded_files = request.files.getlist("file")
    print(uploaded_files)
    # save image to static folder
    for image in uploaded_files:
        print(image.filename)
        image.save('static/chapter-icons/'+image.filename)
    return redirect('/adminpanel')
@app.route('/adminpanel/uploadsidepage',methods=['POST'])
@admin_auth
def UploadSidePage():
    # get image from form
    uploaded_files = request.files.getlist("file")
    print(uploaded_files)
    # save image to static folder
    for image in uploaded_files:
        print(image.filename)
        image.save('static/side-pages/'+image.filename)
    return redirect('/adminpanel')
@app.route('/adminpanel/delete',methods=['POST'])
@admin_auth
def DeleteComic():
    # get id from form
    id = request.form.get('id')
    # delete from database
    conn = get_connection()
    conn.execute('DELETE FROM comics WHERE rowid=?', (id,))
    conn.commit()
    print("comic deleted")
    return redirect('/adminpanel')
@app.route('/adminpanel/chapteradd',methods=['POST'])
@admin_auth
def AddChapter():
    # get image path and description from form
    web_path = request.form.get('web_path')
    image_path = request.form.get('image_path')
    name = request.form.get('name') or "..."
    print(image_path + name)
    # insert into database
    conn = get_connection()
    conn.execute('INSERT INTO chapters VALUES (?, ?, ?)', (web_path,image_path, name))
    conn.commit()
    print("chapter added")
    return redirect('/adminpanel')
@app.route('/adminpanel/chapteredit',methods=['POST'])
@admin_auth
def EditChapter():
    print("edit chapter")
    # get id, image path, and description from form
    web_path = request.form.get('web_path')
    image_path = request.form.get('image_path')
    name = request.form.get('name') or "..."
    # update database
    conn = get_connection()
    conn.execute('UPDATE chapters SET image_path=?, name=? WHERE webpage=?', (image_path, name, web_path))
    conn.commit()
    print("chapter edited")
    return redirect('/adminpanel')
@app.route('/adminpanel/chapterdelete',methods=['POST'])
@admin_auth
def DeleteChapter():
    # get id from form
    web_path = request.form.get('web_path')
    # delete from database
    conn = get_connection()
    conn.execute('DELETE FROM chapters WHERE webpage=?', (web_path,))
    conn.commit()
    print("chapter deleted")
    return redirect('/adminpanel')

@app.route('/adminpanel/createsidecomic',methods=['POST'])
@admin_auth
def CreateSideComic():
    name = request.form.get('name')
    filename = request.form.get('filename')
    banner_image = request.form.get('image_path')
    description = request.form.get('description') or "A side comic."
    # create database
    conn = alternate_connection('./side-content-data/'+filename+'.db')
    conn.execute('CREATE TABLE IF NOT EXISTS comics (rowid INTEGER PRIMARY KEY, image_path TEXT, description TEXT)')
    conn.commit()
    # make data json file
    data = {
        'name': name,
        'banner_image': banner_image,
        'description': description,
        'filename': filename
    }
    with open('./side-content-data/'+filename+'.json', 'w') as outfile:
        json.dump(data, outfile)


    print("side comic created")
    return redirect('/adminpanel')
@app.route("/adminpanel/editsidedata",methods=['POST'])
@admin_auth
def EditSideData():
    name = request.form.get('name')
    filename = request.form.get('filename')
    banner_image = request.form.get('image_path') or "placeholder.png"
    description = request.form.get('description') or "A side comic."
    # make data json file
    data = {
        'name': name,
        'filename': filename,
        'banner_image': banner_image,
        'description': description
    }
    with open('./side-content-data/'+filename+'.json', 'w') as outfile:
        json.dump(data, outfile)
    print("side comic data edited")
    return redirect('/adminpanel')
@app.route("/adminpanel/sideaddpage",methods=['POST'])
@admin_auth
def SideAddPage():
    name = request.form.get('filename')
    image_path = request.form.get('image_path') or "placeholder.png"
    description = request.form.get('description') or "..."
    conn = get_side_db(name)
    conn.execute('INSERT INTO comics VALUES (NULL, ?, ?)', (image_path, description))
    conn.commit()
    print("side comic page added")
    return redirect('/adminpanel')
@app.route("/adminpanel/sideeditpage",methods=['POST'])
@admin_auth
def SideEditPage():
    name = request.form.get('filename')
    id = request.form.get('id')
    image_path = request.form.get('image_path') or "placeholder.png"
    description = request.form.get('description') or "..."
    conn = get_side_db(name)
    conn.execute('UPDATE comics SET image_path=?, description=? WHERE rowid=?', (image_path, description, id))
    conn.commit()
    print("side comic page edited")
    return redirect('/adminpanel')
@app.route("/adminpanel/uploadcharacter",methods=['POST'])
@admin_auth
def UploadCharacter():
    uploaded_files = request.files.getlist("file")
    print(uploaded_files)
    for image in uploaded_files:
        print(image.filename)
        image.save('static/characters/'+image.filename)
    return redirect('/adminpanel')
@app.route("/adminpanel/addcharacter",methods=['POST'])
@admin_auth
def AddCharacter():
    name = request.form.get('name')
    file = get_character_directory()
    data = json.load(file)
    print(data)
    data['characters'].append(name)
    file.seek(0)
    file.write(json.dumps(data))
    print("character added")
    return redirect('/adminpanel')
@app.route("/adminpanel/deletecharacter",methods=['POST'])
@admin_auth
def DeleteCharacter():
    name = request.form.get('name')
    file = get_character_directory()
    data = json.load(file)
    if not name in data:
        return make_response("Character not found",404)
    data['characters'].remove(name)
    file.seek(0)
    file.write(json.dumps(data))
    print("character deleted")
    return redirect('/adminpanel')
#endregion

#region pages

@app.route("/pages")
def viewpages():
   
    allpages =  get_connection().execute("SELECT * FROM COMICS").fetchall()
    print(allpages)
    return render_template('viewpages.html',pages=allpages)

@app.route("/characters")
def Characters():
    file = get_character_directory()
    data = json.load(file)
    return render_template('characters.html',characters=data['characters'])

@app.route('/<chapter>')
def direct(chapter):
    if chapter == "comic":
        return redirect('/comic')
    if chapter.isdigit():
        issue = int(chapter)
        highest_issue = get_connection().execute('SELECT COUNT(*) FROM comics').fetchone().get('COUNT(*)')
        print(highest_issue)
        if highest_issue < issue:
            return make_response("Not Found (not a chapter)",404)
        return redirect('/comic/'+str(issue))
    if get_side_db(chapter) != None:
        return side_comic_read(chapter,1)
    return page_not_found(404)

@app.route('/<chapter>/<int:issue>')
def direct_sidecomic(chapter,issue):
    if get_side_db(chapter) != None:
        return side_comic_read(chapter,issue)
    return page_not_found(404)

@app.route('/<chapter>/last')
def last_sidecomic(chapter):
    if get_side_db(chapter) != None:
        return side_comic_read(chapter,"HIGH")
@app.route('/<chapter>/first')
def first_sidecomic(chapter):
    if get_side_db(chapter) != None:
        return side_comic_read(chapter,1)

def side_comic_read(chapter,issue):
    conn = get_side_db(chapter)
    highest_issue = conn.execute('SELECT COUNT(*) FROM comics').fetchone().get('COUNT(*)')
    if issue == "HIGH":
        return redirect('/'+chapter+'/'+str(highest_issue))
    if issue > highest_issue:
        return page_not_found(404)
    comic = conn.execute('SELECT * FROM comics WHERE rowid=?', (issue,)).fetchone()
    image_path = comic.get('image_path') or 'placeholder.png'
    row_id = comic.get('rowid') or 1
    data = None
    # get json file and load data
    with open('./side-content-data/'+chapter+'.json') as json_file:
        data = json.load(json_file)
        print(data)
    print(highest_issue)
    comname = data.get('name') or "Side Comic"
    fn = data.get('filename')
    desc = comic.get('description') or "..."
    return render_template('view_side.html',d=desc,p=image_path,issue=issue,high=highest_issue,comname=comname,filename=fn)
    


def get_side_db(id):
    if os.path.isfile('./side-content-data/'+id+'.db'):
        return alternate_connection('./side-content-data/'+id+'.db')
    return None

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404




def administrator_check(data):
    return data.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE')



def setup_tables():
    conn.execute('CREATE TABLE IF NOT EXISTS comics (rowid INTEGER PRIMARY KEY, image_path TEXT, description TEXT,tags JSON, time_published BIGINT)')
    conn.execute('CREATE TABLE IF NOT EXISTS chapters (webpage TEXT,image_path TEXT, name TEXT)')


def setup_app():
    fcheck = os.path.exists
    setup_tables()

    if fcheck('./characters.json') == False:
        with open('characters.json', 'w') as outfile:
            json.dump({"characters":[]}, outfile)
    # check for directories
    checks = ['./static','./static/comic-pages','./static/chapter-icons','./static/side-pages','./static/characters', './side-content-data','page-data' ]
    for directory in checks:
        if fcheck(directory) == False:
            os.mkdir(directory)
    # check for side comic databases

if __name__ == '__main__':
    # create sql database called comics with an id, image path, and description
    setup_app()
    app.run(debug=True)
    
