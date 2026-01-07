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
        # Cas 1 : C'est l'Administrateur
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['user_type'] = 'admin'  # On note que c'est l'admin
            return redirect(url_for('lecture'))
            
        # Cas 2 : C'est l'Utilisateur simple (Exercice 2)
        elif request.form['username'] == 'user' and request.form['password'] == '12345':
            session['user_type'] = 'user'   # On note que c'est un user simple
            return redirect(url_for('search_nom')) # On le renvoie vers sa page dédiée
            
        # Cas 3 : Identifiants incorrects
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
    # --- PROTECTION (Exercice 2) ---
    # On vérifie si l'utilisateur est bien connecté en tant que 'user' (ou 'admin')
    user_type = session.get('user_type')
    if not user_type:
        return redirect(url_for('authentification'))
    
    # --- TRAITEMENT DU FORMULAIRE (Exercice 1) ---
    if request.method == 'POST':
        nom_recherche = request.form['nom']
        
        conn = sqlite3.connect('database.db')
        # On utilise row_factory pour pouvoir appeler les colonnes par leur nom
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        # Requête SQL pour chercher par nom
        cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom_recherche,))
        data = cursor.fetchall()
        conn.close()
        
        # On réutilise le template d'affichage existant pour montrer le résultat
        return render_template('read_data.html', data=data)

    # Si c'est un GET, on affiche le formulaire de recherche
    return render_template('formulaire_recherche.html')

if __name__ == "__main__":
    app.run(debug=True)
