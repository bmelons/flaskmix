from flask import Flask, render_template, request, make_response, redirect
import sqlite3
import os
import json
import dotenv


app = Flask(__name__)
# set static folder
app._static_folder = 'static'
dotenv.load_dotenv()



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

conn = get_connection()
conn.execute('CREATE TABLE IF NOT EXISTS comics (rowid INTEGER PRIMARY KEY, image_path TEXT, description TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS chapters (webpage TEXT,image_path TEXT, name TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS characters (rowid INTEGER PRIMARY KEY, name TEXT, description TEXT, image_path TEXT)')
# index
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',sitename=os.getenv("SITE_TITLE"))

@app.route('/chapters')
def chapters():
    # get list of chapter from comic db
    chapters = get_connection().execute('SELECT * FROM chapters').fetchall()

    # get number of highest issue
    return render_template('chapters.html',sitename=os.getenv("SITE_TITLE"),chapters=chapters)

@app.route('/comic')
def comic():
    return redirect('/comic/1')

@app.route('/socialmedia')
def socialmedia():
    return render_template('socialmedia.html',sitename=os.getenv("SITE_TITLE"))

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
    return render_template('comic.html',sitename=os.getenv("SITE_TITLE"),d=desc,p=image_path,issue=issue,high=highest_issue)
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
    return render_template('sidecontent.html',sitename=os.getenv("SITE_TITLE"),chapters=chapters)


# admin pages
@app.route('/admin',methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        print(request.form.get('username'))
        if request.form.get('username') != os.getenv('COMIC_ADMIN_UNAME'):
            return render_template('admin.html',sitename=os.getenv("SITE_TITLE"),message='Incorrect.')
        if request.form.get('password') != os.getenv('COMIC_ADMIN_PW'):
            return render_template('admin.html',sitename=os.getenv("SITE_TITLE"),message='Incorrect.')
        
        resp = make_response(redirect('/adminpanel'))
        resp.set_cookie('user', os.getenv('COMIC_ADMIN_COOKIE'))
        return resp
    return render_template('admin.html',sitename=os.getenv("SITE_TITLE"))

@app.route('/adminpanel',methods=['GET','POST'])
def adminpanel():
    # check if cookie is right
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
        return make_response("Unauthorized",401)

    # get comics from database
    comics = get_connection().execute('SELECT * FROM comics').fetchall()
    chapters = get_connection().execute('SELECT * FROM chapters').fetchall()
    return render_template('adminpanel.html',comics=comics,chapters=chapters)

@app.route('/adminpanel/add',methods=['POST'])
def AddComic():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
        return make_response("Unauthorized",401)
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
def MassAddComic():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
        return make_response("Unauthorized",401)
    low = int(request.form.get('low'));
    high = int(request.form.get('high'));
    highest_issue = get_connection().execute('SELECT COUNT(*) FROM comics').fetchone().get('COUNT(*)')
    conn = get_connection()
    for i in range(low,high+1):
        image_path = str(i) + ".png"
        description = " "
        conn.execute('INSERT INTO comics VALUES (NULL, ?, ?)', (image_path, description))
    conn.commit()
    print("comics added")
    return redirect('/adminpanel')

@app.route('/adminpanel/edit',methods=['POST'])
def EditComic():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
        return make_response("Unauthorized",401)
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
def UploadToStatic():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE') :
        return make_response("Unauthorized",401)
    # get image from form
    uploaded_files = request.files.getlist("file")
    print(uploaded_files)
    # save image to static folder
    for image in uploaded_files:
        print(image.filename)
        image.save('static/comic-pages/'+image.filename)
    return redirect('/adminpanel')
@app.route('/adminpanel/uploadchaptericon',methods=['POST'])
def UploadChapterIcon():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE') :
        return make_response("Unauthorized",401)
    # get image from form
    uploaded_files = request.files.getlist("file")
    print(uploaded_files)
    # save image to static folder
    for image in uploaded_files:
        print(image.filename)
        image.save('static/chapter-icons/'+image.filename)
    return redirect('/adminpanel')
@app.route('/adminpanel/uploadsidepage',methods=['POST'])
def UploadSidePage():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE') :
        return make_response("Unauthorized",401)
    # get image from form
    uploaded_files = request.files.getlist("file")
    print(uploaded_files)
    # save image to static folder
    for image in uploaded_files:
        print(image.filename)
        image.save('static/side-pages/'+image.filename)
    return redirect('/adminpanel')
@app.route('/adminpanel/delete',methods=['POST'])
def DeleteComic():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
        return make_response("Unauthorized",401)
    # get id from form
    id = request.form.get('id')
    # delete from database
    conn = get_connection()
    conn.execute('DELETE FROM comics WHERE rowid=?', (id,))
    conn.commit()
    print("comic deleted")
    return redirect('/adminpanel')
@app.route('/adminpanel/chapteradd',methods=['POST'])
def AddChapter():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
        return make_response("Unauthorized",401)
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
def EditChapter():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
        return make_response("Unauthorized",401)
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
def DeleteChapter():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
        return make_response("Unauthorized",401)
    # get id from form
    web_path = request.form.get('web_path')
    # delete from database
    conn = get_connection()
    conn.execute('DELETE FROM chapters WHERE webpage=?', (web_path,))
    conn.commit()
    print("chapter deleted")
    return redirect('/adminpanel')

@app.route('/adminpanel/createsidecomic',methods=['POST'])
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
def EditSideData():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
        return make_response("Unauthorized",401)
    name = request.form.get('name')
    filename = request.form.get('filename')
    banner_image = request.form.get('banner_image') or "placeholder.png"
    description = request.form.get('description') or "A side comic."
    # make data json file
    data = {
        'name': name,
        'banner_image': banner_image,
        'description': description
    }
    with open('./side-content-data/'+filename+'.json', 'w') as outfile:
        json.dump(data, outfile)
    print("side comic data edited")
    return redirect('/adminpanel')
@app.route("/adminpanel/sideaddpage",methods=['POST'])
def SideAddPage():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
        return make_response("Unauthorized",401)
    name = request.form.get('filename')
    image_path = request.form.get('image_path') or "placeholder.png"
    description = request.form.get('description') or "..."
    conn = get_side_db(name)
    conn.execute('INSERT INTO comics VALUES (NULL, ?, ?)', (image_path, description))
    conn.commit()
    print("side comic page added")
    return redirect('/adminpanel')
@app.route("/adminpanel/sideeditpage",methods=['POST'])
def SideEditPage():
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
        return make_response("Unauthorized",401)
    name = request.form.get('filename')
    id = request.form.get('id')
    image_path = request.form.get('image_path') or "placeholder.png"
    description = request.form.get('description') or "..."
    conn = get_side_db(name)
    conn.execute('UPDATE comics SET image_path=?, description=? WHERE rowid=?', (image_path, description, id))
    conn.commit()
    print("side comic page edited")
    return redirect('/adminpanel')


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
    return render_template('view_side.html',sitename=os.getenv("SITE_TITLE"),d=desc,p=image_path,issue=issue,high=highest_issue,comname=comname,filename=fn)
    


def get_side_db(id):
    if os.path.isfile('./side-content-data/'+id+'.db'):
        return alternate_connection('./side-content-data/'+id+'.db')
    return None

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html',sitename=os.getenv("SITE_TITLE")), 404

if __name__ == '__main__':
    # create sql database called comics with an id, image path, and description
    app.run(debug=True,host="0.0.0.0")
    

