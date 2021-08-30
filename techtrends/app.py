import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, current_app, g
from werkzeug.exceptions import abort

class DBConnectionManager:
    def __init__(self):
        # Initialize a new db connetion manager.
        # database.db is the sqlite3 database file assigned to the object.
        # self.num_connections is the manager wide number of connections.
        self.db_name = 'database.db'
        self.num_connections = 0


    def new_db_connection(self):
        # Connect to the database
        # if the db does not exist, log an error and return None        
        try:
            connection = sqlite3.connect('database.db')
        except Exception as e:
            logging.debug('Error connecting to database: %s', e)
            return None

        connection.row_factory = sqlite3.Row

        # increment the number of connections
        self.num_connections = self.num_connections + 1
        return connection

    def close_db_connection(self, connection):
        connection.close()
        return connection

    # Function to get a post using its ID
    def get_post(self, post_id):
        connection = self.new_db_connection()
        post = connection.execute('SELECT * FROM posts WHERE id = ?',
                            (post_id,)).fetchone()
        if(post):
            logging.debug('Article "%s" retrieved from database with ID [%s]', str(post["title"]), str(post["id"]))
            connection.close()
            return post
        else:
            logging.debug('Article with ID [%s] not found in database, 404 page loaded', str(post_id))
            return None

    # Funection to get database metrics
    def get_metrics(self):
        connection = db.new_db_connection()
        post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
        # SQLlite database connection count
        dbc_count = db.num_connections
        db.close_db_connection(connection)

        system_metrics = {'post_count': post_count, 'db_connection_count': dbc_count}
        return system_metrics


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
db = DBConnectionManager()

# Define the main route of the web application 
@app.route('/')
def index():
    connection = db.new_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    db.close_db_connection(connection)
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = db.get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.debug('About Us page requested')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = db.new_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            logging.debug('Article "%s" created!', str(title))
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# Define the post creation functionality 
@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({'result': 'OK - healthy'}),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/metrics')
def metrics():
    system_metrics = db.get_metrics()
    response = app.response_class(
        response=json.dumps(system_metrics),
        status=200,
        mimetype='application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
    # logger to stdout and stderr to app.log file with debug level
    logging.basicConfig(
        level=logging.DEBUG, 
        filename='app.log', 
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt= '%d/%m/%Y %I:%M:%S %p',
        )
    app.run(host='0.0.0.0', port='3111')
