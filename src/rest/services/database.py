# TODO https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3

def setup_db():
    import sqlite3

    connection = sqlite3.connect('database.db')


    with open('database.sql') as f:
        connection.executescript(f.read())

    cur = connection.cursor()

    cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
                ('First Post', 'Content for the first post')
                )

    cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
                ('Second Post', 'Content for the second post')
                )

    connection.commit()
    connection.close()

def get_db_connection():
    import sqlite3
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    #if post is None:
        #abort(404)
    return post

def create(data):
    title = data['title']
    content = data['content']
    conn = get_db_connection()
    conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                    (title, content))
    conn.commit()
    conn.close()

def edit(id, data):
    post = get_post(id)
    title = data['title']
    content = data['content']
    conn = get_db_connection()
    conn.execute('UPDATE posts SET title = ?, content = ?'
                 ' WHERE id = ?',
                (title, content, id))
    conn.commit()
    conn.close()

def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
