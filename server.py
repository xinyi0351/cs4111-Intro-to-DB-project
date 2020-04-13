
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os, datetime
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash
#from flask_sqlalchemy import SQLAlchemy

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = "wow very secret wow"


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@35.243.220.243/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.243.220.243/proj1part2"
#
DATABASEURI = "postgresql://mlb2249:2910@35.231.103.173/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
        id serial,
        name text
        ); """)
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')


@app.route('/home', methods=['GET'])
def home():
  if session.get('logged_in'):
    return render_template('search.html')
  else:
    return render_template('index.html')

@app.route('/login', methods={'POST','GET'})
def login():
    if request.method=='POST':
      username  =request.form['username']
      password = request.form['password']
      result = engine.execute("SELECT * FROM member WHERE Username = \'%s\'" %(request.form['username']))
      true = engine.execute("SELECT password FROM member WHERE Username = \'%s\'" %(request.form['username']))
      if result.rowcount > 0 and password != true.first()[0]:
        flash('Wrong password. Try again!')
        return render_template('login.html')
      if result.rowcount <= 0:
        flash("Seems like we don't know you yet. Why don't you register first?")
        return render_template('login.html') 
      session['username'] = request.form['username']
      session['logged_in'] = True
      session['user'] = {'Username': request.form['username']}
      return home()
    else:
      return render_template('login.html')

@app.route('/register', methods={'POST','GET'})
def register():
    if request.method=='POST':
      password  =request.form['password']
      passwordcomfirm = request.form['passwordcomfirm']
      if password != passwordcomfirm:
        flash('Sorry you just entered different passwords.')
        return render_template('register.html')
      result = engine.execute("SELECT * FROM member WHERE User_Id = \'%s\'" %(request.form['userid']))
      if result.rowcount >0:
        flash("Oops. The ID is taken!")
        return render_template('register.html')
      result = engine.execute("SELECT * FROM member WHERE Username = \'%s\'" %(request.form['username']))
      if result.rowcount >0:
        flash("Oops. The username is taken")
        return render_template('register.html')
      engine.execute("INSERT INTO member (User_Id,Username, Birthday, Password) VALUES (\'%s\',\'%s\',\'%s\',\'%s\')" %(request.form['userid'],request.form['username'],request.form['Birthday'], password))
      session['username'] = request.form['username']
      session['logged_in'] = True
      session['user'] = {'Username': request.form['username']}
      return home()
    else:
      return render_template('register.html')

@app.route('/musicsearch', methods=['GET'])
def musicsearch():
    if request.method == 'GET':
        return render_template("musicsearch.html")


@app.route('/lookup', methods=['POST', 'GET'])
def lookup():

    if request.method == 'POST':
        entry = request.form['entry']

        error = 0
        if not entry:
            error = 'Please enter a search term'

        # lookup artist
        cursor = g.conn.execute("SELECT artist_name FROM artist WHERE artist_name = (%s)", entry)

        artist = cursor.fetchall()
        cursor.close()

        # lookup album
        cursor = g.conn.execute("SELECT album_name, artist_name FROM album AS al, creates_album AS c, artist AS ar WHERE al.album_id = c.album_id AND c.artist_id = ar.artist_id AND al.album_name = (%s)", entry)

        album = cursor.fetchall()
        cursor.close()

        # lookup song
        cursor = g.conn.execute("SELECT song_name, artist_name FROM song AS so, perform AS p, artist AS ar WHERE so.song_id = p.song_id AND p.artist_id = ar.artist_id AND so.song_name = (%s)", entry)

        song = cursor.fetchall()
        cursor.close()

        if error:
            flash(error)

        return render_template("lookup.html", artist=artist, album=album, song=song)
    else:
        return render_template("lookup.html")

@app.route('/artview', methods = ['POST', 'GET'])
def artview():

    #show list of all songs and albums by an artist
    if request.method == 'POST':
        artist = request.form['artist']

        error = 0
        if not artist:
            error = 'Please enter an artist'

        #get table of songs and corresponding albums by artist
        cursor = g.conn.execute("SELECT song_name, album_name, song.published_date FROM artist, perform, song, contains, album WHERE artist.artist_id = perform.artist_id AND song.song_id = perform.song_id AND song.song_id = contains.song_id AND album.album_id = contains.album_id AND artist.artist_name = (%s)", artist)
        
        artistres = cursor.fetchall()
        cursor.close()
        
        if not artistres:
            error = 'No results'

        #get table of musicians who are members of the artist
        cursor = g.conn.execute("SELECT name, role, artist_name FROM artist AS ar, member_of AS m, musician AS mu WHERE ar.artist_id = m.artist_id AND m.musician_id = mu.musician_id AND ar.artist_name = (%s)", artist)
        
        musicians = cursor.fetchall()
        cursor.close()
        
        error2 = 0
        if not musicians:
            error2 = 'No musicians listed'

        if error:
            flash(error)

        if error2:
            flash(error2)

        return render_template("artview.html", artistres = artistres, musicians = musicians)
    else:
        return render_template("artview.html")


@app.route('/albview', methods = ['POST', 'GET'])
def albview():

    #show list of all songs and albums by an artist
    if request.method == 'POST':
        album = request.form['album']

        error = 0
        if not album:
            error = 'Please enter an album'

        #get table of all songs in album and artist who wrote album 
        cursor = g.conn.execute("SELECT song_name, album_name, artist_name FROM song AS so, contains AS c, album AS al, creates_album AS ca, artist AS ar WHERE so.song_id = c.song_id AND c.album_id = al.album_id AND al.album_id = ca.album_id AND ca.artist_id = ar.artist_id AND al.album_name = (%s)", album)

        albumres = cursor.fetchall()
        cursor.close()

        if not albumres:
            error = 'No results'

        if error:
            flash(error)

        return render_template("albview.html", albumres = albumres)
    else:
        return render_template("albview.html")
 

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
