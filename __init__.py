from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def est_authentifie():
    return session.get('authentifie')

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
      
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['user_type'] = 'admin'  # On note que c'est l'admin
            return redirect(url_for('lecture'))
            
      
        elif request.form['username'] == 'user' and request.form['password'] == '12345':
            session['user_type'] = 'user'   # On note que c'est un user simple
            return redirect(url_for('search_nom')) # On le renvoie vers sa page dédiée
            
      
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')

@app.route('/fiche_nom/', methods=['GET', 'POST'])
def search_nom():
   
 
    user_type = session.get('user_type')
    if not user_type:
        return redirect(url_for('authentification'))
    
   
    if request.method == 'POST':
        nom_recherche = request.form['nom']
        
        conn = sqlite3.connect('database.db')
        # On utilise row_factory pour pouvoir appeler les colonnes par leur nom
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        
        cursor.execute('SELECT * FROM clients WHERE UPPER(nom) = UPPER(?)', (nom_recherche,))
        data = cursor.fetchall()
        conn.close()
        
        
        return render_template('read_data.html', data=data)

   
    return render_template('formulaire_recherche.html')

if __name__ == "__main__":
    app.run(debug=True)
