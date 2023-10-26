from flask import Flask, render_template, request, make_response, redirect
import sqlite3
import os
import dotenv


app = Flask(__name__)
# set static folder
app._static_folder = 'static'
dotenv.load_dotenv()


def get_connection():
    conn = sqlite3.connect('comic.db')
    conn.row_factory = dict_factory
    return conn
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = get_connection()
conn.execute('CREATE TABLE IF NOT EXISTS comics (rowid INTEGER PRIMARY KEY, image_path TEXT, description TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS chapters (webpage TEXT,image_path TEXT, name TEXT)')
# index
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/chapters')
def chapters():
    # get list of chapter from comic db
    comics = get_connection().execute('SELECT * FROM comics').fetchall()
    # get number of highest issue
    return render_template('chapters.html',comics=comics)

@app.route('/comic')
def comic():
    return redirect('/comic/1')

@app.route('/socialmedia')
def socialmedia():
    return render_template('socialmedia.html')

@app.route('/comic/<int:issue>')
def comic_issue(issue):
    highest_issue = get_connection().execute('SELECT COUNT(*) FROM comics').fetchone().get('COUNT(*)')
    if issue > highest_issue:
        return make_response("Not Found (not a page)",404)
    # render comic template if issue is in database
    comic = get_connection().execute('SELECT * FROM comics WHERE rowid=?', (issue,)).fetchone()
    # return str(comic)
    # get number of highest issue
    image_path = comic.get('image_path') or 'placeholder.png'
    row_id = comic.get('rowid') or 0
    print(highest_issue)
    return render_template('comic.html',p=image_path,issue=issue,high=highest_issue)

# admin pages
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
def adminpanel():
    # check if cookie is right
    if request.cookies.get('user') != os.getenv('COMIC_ADMIN_COOKIE'):
        return make_response("Unauthorized",401)

    # get comics from database
    comics = get_connection().execute('SELECT * FROM comics').fetchall()
    return render_template('adminpanel.html',comics=comics)

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
        image.save('static/'+image.filename)
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
    image_path = request.form.get('image_path')
    name = request.form.get('description') or "..."
    print(image_path + name)
    # insert into database
    conn = get_connection()
    conn.execute('INSERT INTO chapters VALUES (NULL, ?, ?)', (image_path, name))
    conn.commit()
    print("chapter added")
    return redirect('/adminpanel')


if __name__ == '__main__':
    # create sql database called comics with an id, image path, and description
    app.run(debug=True)
    

