from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour créer une clé "authentifie" dans la session utilisateur
def est_authentifie():
    return session.get('authentifie')

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        # Rediriger vers la page d'authentification si l'utilisateur n'est pas authentifié
        return redirect(url_for('authentification'))

  # Si l'utilisateur est authentifié
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Cas 1 : Connexion Admin
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            session['username'] = 'admin' # On stocke le nom pour vérifier plus tard
            return redirect(url_for('lecture'))
            
        # Cas 2 : Connexion User (Exercice 2)
        elif username == 'user' and password == '12345':
            session['logged_in'] = True
            session['username'] = 'user' # On stocke 'user'
            return redirect(url_for('lecture'))
            
        else:
            return "Identifiants incorrects"
    return render_template('authentification.html')

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    # Rendre le template HTML et transmettre les données
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
    return render_template('formulaire.html')  # afficher le formulaire

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']

    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Exécution de la requête SQL pour insérer un nouveau client
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')  # Rediriger vers la page d'accueil après l'enregistrement
                                                                                                                                       
if __name__ == "__main__":
  app.run(debug=True)

@app.route('/fiche_nom/<string:nom>')
def fiche_nom(nom):
    # VERIFICATION : Est-ce que quelqu'un est connecté ? 
    # ET est-ce que c'est bien l'utilisateur 'user' ?
    if not session.get('logged_in') or session.get('username') != 'user':
        # Si ce n'est pas le cas, on bloque l'accès (Erreur 403 : Interdit)
        return "Accès réservé exclusivement à l'utilisateur 'user'.", 403

    # Si le code arrive ici, c'est que l'utilisateur est bien 'user'
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom,))
    data = cursor.fetchall()
    conn.close()
    
    return render_template('read_data.html', data=data)
    
@app.route('/fiche_nom/<string:nom>')
def fiche_nom(nom):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Utilise fetchall() pour toujours avoir une liste, 
    # même s'il n'y a qu'un seul résultat
    cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom,))
    clients_trouves = cursor.fetchall() 
    conn.close()
    
    if clients_trouves:
        # IMPORTANT : on passe la liste 'clients_trouves' à la variable 'data'
        return render_template('read_data.html', data=clients_trouves)
    else:
        return "Client non trouvé", 404
