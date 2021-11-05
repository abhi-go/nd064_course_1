import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# import default dict
from collections import defaultdict

# track performance stats
perf_stats = defaultdict(int)


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global perf_stats
    perf_stats['db_connection_count'] += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    perf_stats['get_post_count'] += 1
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s: %(module)s: %(message)s',
    }},
    'handlers': {
          'stdout': {
              'class': 'logging.StreamHandler',
              'stream': 'ext://sys.stdout',
              'formatter': 'default'
          },
          'stderr': {
              'class': 'logging.StreamHandler',
              'stream': 'ext://sys.stderr',
              'formatter': 'default'
          },
     },
    'root': {
        'level': 'DEBUG',
        'handlers': ['stdout', 'stderr']
    }
})

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

## ADD implementations

## Check the health
@app.route('/healthz')
def healthz():
    return jsonify({'result': 'OK - healthy'})

def get_num_posts():
    connection = get_db_connection()
    num_posts = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()
    return num_posts


## Get the metrics
@app.route('/metrics')
def metrics():
    global perf_stats
    d = {}
    d['post_count'] = get_num_posts()
    d.update(perf_stats)
    return jsonify(d)


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    post_id_name = 'get_post_id_{}_count'.format(post_id)
    perf_stats[post_id_name] += 1

    if post is None:
      app.logger.info("Non existing article: %d accessed", post_id)
      return render_template('404.html'), 404
    else:
      app.logger.info("Article: %s retrieved!", post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    perf_stats['about_page'] += 1
    app.logger.info("about us accessed")
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
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info("new post: %s created", title)

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
