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

        context = dict(data = output)

        return render_template("index.html", **context)




