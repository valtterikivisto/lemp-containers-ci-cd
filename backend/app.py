from flask import Flask, jsonify, request
import os
import mysql.connector

#flask app instance update joo
app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'db')
DB_USER = os.getenv('DB_USER', 'appuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'changeme')
DB_NAME = os.getenv('DB_NAME', 'appdb')

@app.get('/api/health')
def health():
    return jsonify(message={'status': 'ok'})

@app.get('/api/time')
def time():
    # Placeholder for actual time fetching logic
    #get server time from db
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )
    cur = conn.cursor()
    cur.execute("SELECT NOW()")
    row = cur.fetchone()
    cur.close(); conn.close()
    return jsonify(message={'time': row[0]})

@app.get('/api')
def index():
    """Simple endpoint that greets from DB."""
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )
    cur = conn.cursor()
    cur.execute("SELECT 'Hello from MySQL via Testi!'")
    row = cur.fetchone()
    cur.close(); conn.close()
    return jsonify(message=row[0])

@app.get('/api/users/init')
def users():
    """Create users table"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100))")
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Database initialized"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post('/api/users')
def create_user():
    """Create a user"""
    try:
        data = request.json
        username = data.get('username')

        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name) VALUES (%s)", (username,))   
        new_user_id = cursor.lastrowid

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({
            "message": f"User '{username}' created successfully!",
            "id": new_user_id,
            "username": username,
            "status": "success"
        }), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "User might already exist"}), 400
    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Database error: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    
@app.get('/api/users')
def get_users():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        cursor.close()
        conn.close()
        return jsonify({"users": users})
    except Exception as e:
        return jsonify({"error": str(e)}), 500        
         

if __name__ == '__main__':
    # Dev-only fallback
    app.run(host='0.0.0.0', port=8000, debug=True)

