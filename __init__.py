from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Fonction utilitaire pour se connecter à la BDD
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- AUTHENTIFICATION ---
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Gestion ADMIN
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['user_type'] = 'admin'
            return redirect(url_for('lecture'))
        # Gestion USER (Ajouté pour l'exercice)
        elif request.form['username'] == 'user' and request.form['password'] == '12345':
            session['user_type'] = 'user'
            return redirect(url_for('catalogue'))
        else:
            return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html', error=False)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('hello_world'))

# --- ROUTES GENERALES ---
@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if session.get('user_type') != 'admin':
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié en tant qu'administrateur</h2>"

# --- ROUTES CLIENTS (EXERCICES PRECEDENTS) ---
@app.route('/consultation/')
def ReadBDD():
    conn = get_db_connection()
    clients = conn.execute('SELECT * FROM clients;').fetchall()
    conn.close()
    return render_template('read_data.html', data=clients)

@app.route('/enregistrer_client', methods=['GET', 'POST'])
def enregistrer_client():
    if request.method == 'GET':
        return render_template('formulaire.html')
    
    nom = request.form['nom']
    prenom = request.form['prenom']
    conn = get_db_connection()
    conn.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', 
                 (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')

@app.route('/fiche_nom/', methods=['GET', 'POST'])
def search_nom():
    if not session.get('user_type'):
        return redirect(url_for('authentification'))
    
    if request.method == 'POST':
        nom_recherche = request.form['nom']
        conn = get_db_connection()
        clients = conn.execute('SELECT * FROM clients WHERE UPPER(nom) = UPPER(?)', (nom_recherche,)).fetchall()
        conn.close()
        return render_template('read_data.html', data=clients)

    return render_template('formulaire_recherche.html') # Assure-toi d'avoir ce template

# --- ROUTES BIBLIOTHEQUE (SEQUENCE 6) ---

# 1. Gestion Admin des livres (Ajout / Suppression)
@app.route('/admin_livres', methods=['GET', 'POST'])
def admin_livres():
    if session.get('user_type') != 'admin':
        return redirect(url_for('authentification'))
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        # Statut 0 par défaut (disponible)
        conn.execute('INSERT INTO livres (titre, auteur, statut) VALUES (?, ?, 0)', (titre, auteur))
        conn.commit()
    
    livres = conn.execute('SELECT * FROM livres').fetchall()
    conn.close()
    return render_template('admin_livres.html', livres=livres)

@app.route('/supprimer_livre/<int:id>')
def supprimer_livre(id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('authentification'))
    conn = get_db_connection()
    conn.execute('DELETE FROM livres WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_livres'))

# 2. Catalogue et Emprunts (Pour tout le monde connecté)
@app.route('/catalogue')
def catalogue():
    if not session.get('user_type'):
        return redirect(url_for('authentification'))
        
    conn = get_db_connection()
    livres = conn.execute('SELECT * FROM livres').fetchall()
    conn.close()
    return render_template('catalogue.html', livres=livres)

@app.route('/emprunter/<int:id>')
def emprunter(id):
    if not session.get('user_type'):
        return redirect(url_for('authentification'))
    conn = get_db_connection()
    # On passe le statut à 1 (emprunté)
    conn.execute('UPDATE livres SET statut = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('catalogue'))

@app.route('/rendre/<int:id>')
def rendre(id):
    if not session.get('user_type'):
        return redirect(url_for('authentification'))
    conn = get_db_connection()
    # On repasse le statut à 0 (disponible)
    conn.execute('UPDATE livres SET statut = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('catalogue'))

if __name__ == "__main__":
    app.run(debug=True)
