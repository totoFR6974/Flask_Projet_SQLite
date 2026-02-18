from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# --- CORRECTION 1 : On vérifie maintenant le type d'utilisateur ---
def est_authentifie():
    return session.get('user_type') is not None

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if session.get('user_type') != 'admin':
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié en tant qu'administrateur</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['user_type'] = 'admin'
            # AVANT : return redirect(url_for('lecture'))
            # APRES : On renvoie vers l'accueil ('hello_world')
            return redirect(url_for('hello_world')) 
            
        elif request.form['username'] == 'user' and request.form['password'] == '12345':
            session['user_type'] = 'user'
            # Vous pouvez aussi renvoyer le user vers l'accueil s'il préfère voir le menu
            # return redirect(url_for('hello_world')) 
            return redirect(url_for('search_nom'))
        else:
            return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html', error=False)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('hello_world'))

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

@app.route('/enregistrer_client', methods=['GET', 'POST'])
def enregistrer_client():
    if request.method == 'GET':
        return render_template('formulaire.html')
    
    nom = request.form['nom']
    prenom = request.form['prenom']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')

# --- CORRECTION 2 : Ajout du return pour le mode GET ---
@app.route('/fiche_nom/', methods=['GET', 'POST'])
def search_nom():
    user_type = session.get('user_type')
    if not user_type:
        return redirect(url_for('authentification'))
    
    if request.method == 'POST':
        nom_recherche = request.form['nom']
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE UPPER(nom) = UPPER(?)', (nom_recherche,))
        data = cursor.fetchall()
        conn.close()
        return render_template('read_data.html', data=data)

    return render_template('formulaire_recherche.html')

@app.route('/admin_livres', methods=['GET', 'POST'])
def admin_livres():
    if session.get('user_type') != 'admin':
        return redirect(url_for('authentification'))
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        cursor.execute('INSERT INTO livres (titre, auteur, statut) VALUES (?, ?, 0)', (titre, auteur))
        conn.commit()
    cursor.execute('SELECT * FROM livres')
    livres = cursor.fetchall()
    conn.close()
    return render_template('admin_livres.html', livres=livres)

@app.route('/supprimer_livre/<int:id>')
def supprimer_livre(id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('authentification'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM livres WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_livres'))

@app.route('/catalogue')
def catalogue():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres')
    livres = cursor.fetchall()
    conn.close()
    return render_template('catalogue.html', livres=livres)

@app.route('/emprunter/<int:id>')
def emprunter(id):
    if not session.get('user_type'):
        return redirect(url_for('authentification'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE livres SET statut = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('catalogue'))

@app.route('/rendre/<int:id>')
def rendre(id):
    if not session.get('user_type'):
        return redirect(url_for('authentification'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE livres SET statut = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('catalogue'))

# ==========================================
# MODULE : GESTIONNAIRE DE TACHES (Mini Projet)
# ==========================================

@app.route('/taches')
def taches_index():
    # Vérifie si l'utilisateur est connecté (Admin ou User)
    if not session.get('user_type'):
        return redirect(url_for('authentification'))
    
    conn = get_db_connection()
    # On récupère les tâches, les plus urgentes en premier, puis celles terminées à la fin
    taches = conn.execute('SELECT * FROM taches ORDER BY est_terminee ASC, date_echeance ASC').fetchall()
    conn.close()
    return render_template('taches.html', taches=taches)

@app.route('/taches/ajouter', methods=['POST'])
def ajouter_tache():
    if not session.get('user_type'):
        return redirect(url_for('authentification'))
    
    titre = request.form['titre']
    description = request.form['description']
    date_echeance = request.form['date_echeance']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO taches (titre, description, date_echeance) VALUES (?, ?, ?)',
                 (titre, description, date_echeance))
    conn.commit()
    conn.close()
    return redirect(url_for('taches_index'))

@app.route('/taches/terminer/<int:id>')
def terminer_tache(id):
    if not session.get('user_type'):
        return redirect(url_for('authentification'))
        
    conn = get_db_connection()
    # On passe la tâche à "Terminée" (1)
    conn.execute('UPDATE taches SET est_terminee = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('taches_index'))

@app.route('/taches/supprimer/<int:id>')
def supprimer_tache(id):
    if not session.get('user_type'):
        return redirect(url_for('authentification'))
        
    conn = get_db_connection()
    conn.execute('DELETE FROM taches WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('taches_index'))
    
if __name__ == "__main__":
    app.run(debug=True)
