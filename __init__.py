<!DOCTYPE html>
<html>
<head><title>Catalogue</title></head>
<body>
    <h1>Catalogue Bibliothèque</h1>
    <table border="1">
        <tr>
            <th>Titre</th>
            <th>Auteur</th>
            <th>Etat</th>
            <th>Action</th>
        </tr>
        {% for livre in livres %}
        <tr>
            <td>{{ livre['titre'] }}</td>
            <td>{{ livre['auteur'] }}</td>
            <td>
                {% if livre['statut'] == 0 %}
                    <span style="color:green">Disponible</span>
                {% else %}
                    <span style="color:red">Emprunté</span>
                {% endif %}
            </td>
            <td>
                {% if livre['statut'] == 0 %}
                    <a href="{{ url_for('emprunter', id=livre['id']) }}">Emprunter</a>
                {% else %}
                    <a href="{{ url_for('rendre', id=livre['id']) }}">Rendre</a>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </table>
    <br>
    <a href="{{ url_for('logout') }}">Se déconnecter</a>
</body>
</html>
