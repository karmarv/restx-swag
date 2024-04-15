import sqlite3
import pandas as pd

# TODO https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3

def setup_db():
    connection = sqlite3.connect('database.db')
    with open('database.sql') as f:
        connection.executescript(f.read())
    cur = connection.cursor()
    cur.execute("INSERT INTO images (fullpath, content) VALUES (?, ?)",
                ('/home/rahul/workspace/eyeclimate/restx-swag/data/uploads/black-eye-icon_23-2147493411.jpg', 'Image of an eye icon'))
    cur.execute("INSERT INTO images (fullpath, content) VALUES (?, ?)",
                ('/home/rahul/workspace/eyeclimate/restx-swag/data/swagger-screenshot.png', 'Swagger screenshot'))
    connection.commit()

    connection.close()
    return get_all_df()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get(id):
    conn = get_db_connection()
    img = conn.execute('SELECT * FROM images WHERE id = ?',
                        (id,)).fetchone()
    conn.close()
    #if post is None:
        #abort(404)
    return img

def get_all_df():
    imgs=None
    try:
        conn = get_db_connection()
        imgs = pd.read_sql_query('SELECT * FROM images', conn)
    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if conn:
            conn.close()    
    return imgs


def get_all():
    imgs=None
    try:
        conn = get_db_connection()
        imgs = conn.execute('SELECT * FROM images').fetchall()
    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if conn:
            conn.close()    
    return imgs

def create(data):
    fullpath = data['fullpath']
    content = data['content']
    conn = get_db_connection()
    conn.execute('INSERT INTO images (fullpath, content) VALUES (?, ?)',
                    (fullpath, content))
    conn.commit()
    conn.close()

def edit(id, data):
    post = get(id)
    fullpath = data['fullpath']
    content = data['content']
    conn = get_db_connection()
    conn.execute('UPDATE images SET fullpath = ?, content = ?'
                 ' WHERE id = ?',
                (fullpath, content, id))
    conn.commit()
    conn.close()

def delete(id):
    post = get(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM images WHERE id = ?', (id,))
    conn.commit()
    conn.close()
