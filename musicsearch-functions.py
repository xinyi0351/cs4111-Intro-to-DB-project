"""
   functions needed for interaction with music in database

   to be added to server.py
"""

import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

"""
   sample from server.py
   insertion query

@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

   sample from server.py
   lookup query

@app.route('/')
def index():
 
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

   context = dict(data = names)

  return render_template("index.html", **context)

"""


@app.route('/lookup', methods=['POST'])
def lookup():

    if request.method == 'POST':
        entry = request.form['entry']

        if not entry:
            error = 'Please enter a search term'

        output = []

        # lookup artist
        cursor = g.conn.execute("SELECT artist_name FROM artist WHERE artist_name = (%s)", entry)

        for result in cursor:
            output.append(result[0], " ")
        cursor.close()

        # lookup album
        cursor = g.conn.execute("SELECT album_name, artist_name 
                                FROM album AS al, creates_album AS c, artist AS ar
                                WHERE al.album_id = c.album_id AND c.artist_id = ar.artist_id
                                AND al.album_name = (%s)", entry)

        for result in cursor:
            output.append(result[0], result[1])
        cursor.close()

        # lookup song
        cursor = g.conn.execute("SELECT song_name, artist_name 
                                FROM song AS so, creates_album AS c, artist AS ar
                                WHERE so.song_id = c.song_id AND c.artist_id = ar.artist_id
                                AND so.song_name = (%s)", entry)

        for result in cursor:
            output.append(result[0], result[1])
        cursor.close()

        if not output:
            error = 'No results'

        if error:
            flash(error)

        context = dict(searchresult = output)

        return render_template("index.html", **context)


@app.route('/artview', methods = ['POST'])
def artview():

    #show list of all songs and albums by an artist
    if request.method = 'POST':
        artist = request.form('artist')

        error = 0
        if not artist:
            error = 'Please enter an artist'

        output = []

        #get table of songs and corresponding albums by artist
        cursor = g.conn.execute("SELECT song_name, album_name, song.published_date
                                FROM artist, perform, song, contains, album
                                WHERE artist.artist_id = perform.artist_id AND song.song_id = perform.song_id
                                AND song.song_id = containst.song_id AND album.album_id = contains.album_id
                                AND artist.artist_name = (%s)", artist)
        
        for result in cursor:
            output.append(result[0], result[1], result[2])
        cursor.close()
        
        if not output:
            error = 'No results'

        musicians = []

        #get table of musicians who are members of the artist
        cursor = g.conn.execute("SELECT musician_name, role, artist_name
                                FROM artist AS ar, member_of AS m, musician AS mu
                                WHERE ar.artist_id = m.artist_id AND m.musician_id = mu.musician_id
                                AND ar.artist_name = (%s)", artist)

        for result in cursor:
            musicians.append(result[0], result[1], result[2])
        cursor.close()
        
        error2 = 0
        if not musicians:
            error2 = 'No musicians listed'

        context = dict(artistres = output, artistmsc = musicians)

        return render_template("index.html", **context)




