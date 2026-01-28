from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import datetime # Nécessaire pour gérer les dates d'emprunt

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# --- FONCTION UTILITAIRE POUR LA BDD ---
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom (ex: row['titre'])
    return conn

# --- AUTHENTIFICATION ---
def est_authentifie():
    return session.get('authentifie')

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # 1. Vérification Admin codé en dur (Exercice précédent)
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['authentifie'] = True
            session['user_role'] = 'admin'
            flash("Connexion administrateur réussie.")
            return redirect(url_for('lecture'))
        
        # 2. Vérification Utilisateurs Bibliothèque (Nouvelle fonctionnalité)
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM utilisateurs_biblio WHERE pseudo = ? AND password = ?',
                            (request.form['username'], request.form['password'])).fetchone()
        conn.close()

        if user:
            session['authentifie'] = True
            session['user_role'] = 'admin' if user['est_admin'] else 'user'
            session['user_id'] = user['id'] # On stocke l'ID pour les emprunts
            flash(f"Bienvenue {user['pseudo']} !")
            return redirect(url_for('bibliotheque_accueil'))
        
        # Echec
        return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('hello_world'))

# --- ROUTES DE BASE / CLIENTS (EXERCICES PRECEDENTS) ---

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = get_db_connection()
    client = conn.execute('SELECT * FROM clients WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    return render_template('read_data.html', data=[client] if client else [])

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
    else:
        nom = request.form['nom']
        prenom = request.form['prenom']
        conn = get_db_connection()
        conn.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', 
                     (1002938, nom, prenom, "ICI"))
        conn.commit()
        conn.close()
        return redirect('/consultation/')

@app.route('/fiche_nom/<string:nom>')
def fiche_nom(nom):
    conn = get_db_connection()
    client = conn.execute('SELECT * FROM clients WHERE nom = ?', (nom,)).fetchone()
    conn.close()
    
    if client:
        # Note: Assure-toi d'avoir un template 'fiche_client.html' ou utilise 'read_data.html'
        return render_template('read_data.html', data=[client]) 
    else:
        return "Client non trouvé", 404



@app.route('/bibliotheque')
def bibliotheque_accueil():
    return render_template('bibliotheque/index.html')

# 1. Gestion des Livres (Ajout, Suppression, Recherche)
@app.route('/bibliotheque/livres', methods=['GET', 'POST'])
def gestion_livres():
    conn = get_db_connection()
    
    # Ajout d'un livre
    if request.method == 'POST' and 'ajout_livre' in request.form:
        titre = request.form['titre']
        auteur = request.form['auteur']
        stock = request.form['stock']
        conn.execute('INSERT INTO livres (titre, auteur, stock) VALUES (?, ?, ?)', (titre, auteur, stock))
        conn.commit()
        flash("Livre ajouté !")
    
    # Suppression d'un livre
    if request.method == 'POST' and 'supprimer_livre' in request.form:
        livre_id = request.form['livre_id']
        conn.execute('DELETE FROM livres WHERE id = ?', (livre_id,))
        conn.commit()
        flash("Livre supprimé.")

    # Recherche
    query = request.args.get('q')
    if query:
        livres = conn.execute(
            'SELECT * FROM livres WHERE titre LIKE ? OR auteur LIKE ?', 
            ('%' + query + '%', '%' + query + '%')
        ).fetchall()
    else:
        livres = conn.execute('SELECT * FROM livres').fetchall()
    
    conn.close()
    return render_template('bibliotheque/livres.html', livres=livres)

# 2. Gestion des Utilisateurs Bibliothèque
@app.route('/bibliotheque/utilisateurs', methods=['GET', 'POST'])
def gestion_utilisateurs():
    conn = get_db_connection()
    
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        password = request.form['password']
        est_admin = 1 if 'est_admin' in request.form else 0
        
        try:
            conn.execute('INSERT INTO utilisateurs_biblio (pseudo, password, est_admin) VALUES (?, ?, ?)',
                       (pseudo, password, est_admin))
            conn.commit()
            flash("Utilisateur créé.")
        except sqlite3.IntegrityError:
            flash("Erreur : Ce pseudo existe déjà.")

    users = conn.execute('SELECT * FROM utilisateurs_biblio').fetchall()
    conn.close()
    return render_template('bibliotheque/utilisateurs.html', users=users)

# 3. Emprunt et Retour de livres
@app.route('/bibliotheque/emprunt', methods=['GET', 'POST'])
def emprunt_livre():
    conn = get_db_connection()
    
    # Action d'emprunter
    if request.method == 'POST':
        livre_id = request.form['livre_id']
        user_id = request.form['user_id']
        
        # Vérification du stock
        livre = conn.execute('SELECT stock FROM livres WHERE id = ?', (livre_id,)).fetchone()
        en_pret = conn.execute('SELECT COUNT(*) FROM emprunts WHERE livre_id = ? AND date_retour IS NULL', (livre_id,)).fetchone()[0]
        
        if livre and livre['stock'] > en_pret:
            conn.execute('INSERT INTO emprunts (livre_id, user_id) VALUES (?, ?)', (livre_id, user_id))
            conn.commit()
            flash("Livre emprunté avec succès !")
        else:
            flash("Impossible : Stock épuisé ou livre inexistant.")
            
    # Récupération des données pour l'affichage
    livres = conn.execute('SELECT * FROM livres').fetchall()
    users = conn.execute('SELECT * FROM utilisateurs_biblio').fetchall()
    
    # Liste des emprunts en cours (avec jointures pour avoir les noms)
    emprunts_en_cours = conn.execute('''
        SELECT e.id, l.titre, u.pseudo, e.date_emprunt 
        FROM emprunts e 
        JOIN livres l ON e.livre_id = l.id 
        JOIN utilisateurs_biblio u ON e.user_id = u.id 
        WHERE e.date_retour IS NULL
    ''').fetchall()
    
    conn.close()
    return render_template('bibliotheque/emprunts.html', livres=livres, users=users, emprunts=emprunts_en_cours)

# Route spécifique pour le retour d'un livre (appelée depuis la liste des emprunts)
@app.route('/bibliotheque/retour/<int:emprunt_id>')
def retour_livre(emprunt_id):
    conn = get_db_connection()
    conn.execute('UPDATE emprunts SET date_retour = ? WHERE id = ?', 
               (datetime.datetime.now(), emprunt_id))
    conn.commit()
    conn.close()
    flash("Livre rendu avec succès.")
    return redirect(url_for('emprunt_livre'))


# --- LANCEMENT DE L'APPLICATION ---
if __name__ == "__main__":
    app.run(debug=True)
