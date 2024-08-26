from flask import Blueprint, flash, render_template, request, redirect, url_for
import re
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user, login_manager

auth = Blueprint('auth', __name__)

translations = {
    'English': ['New Conversation', 'Configuration', 'Invalid email address.', 'Email address already in use by another account.', 'Passwords don\'t match.', 'Password must be at least 8 characters long and contain both letters and numbers.', 'First name cannot be empty.', 'Invalid language selected.', 'Your changes have been saved!', 'Configure User', 'Email Address', 'Enter Email', 'Password', 'Enter new password (leave blank to keep current)', 'Password (Confirm)', 'Confirm password', 'First Name', 'Enter first name', 'Preferred Language', 'Save Changes'],
    'Spanish': ['Nueva Conversación', 'Configuración', 'Dirección de correo electrónico inválida.', 'La dirección de correo electrónico ya está en uso por otra cuenta.', 'Las contraseñas no coinciden.', 'La contraseña debe tener al menos 8 caracteres y contener tanto letras como números.', 'El nombre no puede estar vacío.', 'Idioma seleccionado no válido.', '¡Tus cambios han sido guardados!', 'Configurar Usuario', 'Dirección de Correo Electrónico', 'Introducir Correo Electrónico', 'Contraseña', 'Introducir nueva contraseña (dejar en blanco para mantener la actual)', 'Contraseña (Confirmar)', 'Confirmar contraseña', 'Nombre', 'Introducir nombre', 'Idioma Preferido', 'Guardar Cambios'],
    'French': ['Nouvelle Conversation', 'Configuration', 'Adresse e-mail invalide.', 'Adresse e-mail déjà utilisée par un autre compte.', 'Les mots de passe ne correspondent pas.', 'Le mot de passe doit contenir au moins 8 caractères et inclure des lettres et des chiffres.', 'Le prénom ne peut pas être vide.', 'Langue sélectionnée invalide.', 'Vos modifications ont été enregistrées !', 'Configurer l\'Utilisateur', 'Adresse e-mail', 'Entrer l\'adresse e-mail', 'Mot de passe', 'Entrer un nouveau mot de passe (laisser vide pour conserver l\'actuel)', 'Mot de passe (Confirmer)', 'Confirmer le mot de passe', 'Prénom', 'Entrer le prénom', 'Langue Préférée', 'Enregistrer les Modifications'],
    'Portuguese': ['Nova Conversa', 'Configuração', 'Endereço de e-mail inválido.', 'Endereço de e-mail já utilizado por outra conta.', 'As senhas não coincidem.', 'A senha deve ter pelo menos 8 caracteres e conter letras e números.', 'O nome não pode estar vazio.', 'Idioma selecionado inválido.', 'Suas alterações foram salvas!', 'Configurar Usuário', 'Endereço de E-mail', 'Insira o E-mail', 'Senha', 'Insira uma nova senha (deixe em branco para manter a atual)', 'Senha (Confirmar)', 'Confirmar senha', 'Primeiro Nome', 'Insira o primeiro nome', 'Idioma Preferido', 'Salvar Alterações'],
    'Italian': ['Nuova Conversazione', 'Configurazione', 'Indirizzo email non valido.', 'Indirizzo email già in uso da un altro account.', 'Le password non corrispondono.', 'La password deve essere lunga almeno 8 caratteri e contenere sia lettere che numeri.', 'Il nome non può essere vuoto.', 'Lingua selezionata non valida.', 'Le tue modifiche sono state salvate!', 'Configura Utente', 'Indirizzo Email', 'Inserisci Email', 'Password', 'Inserisci una nuova password (lascia vuoto per mantenere quella attuale)', 'Password (Conferma)', 'Conferma password', 'Nome', 'Inserisci il nome', 'Lingua Preferita', 'Salva Modifiche'],
    'German': ['Neues Gespräch', 'Konfiguration', 'Ungültige E-Mail-Adresse.', 'E-Mail-Adresse wird bereits von einem anderen Konto verwendet.', 'Passwörter stimmen nicht überein.', 'Das Passwort muss mindestens 8 Zeichen lang sein und sowohl Buchstaben als auch Zahlen enthalten.', 'Der Vorname darf nicht leer sein.', 'Ungültige Sprache ausgewählt.', 'Ihre Änderungen wurden gespeichert!', 'Benutzer konfigurieren', 'E-Mail-Adresse', 'E-Mail eingeben', 'Passwort', 'Neues Passwort eingeben (leer lassen, um das aktuelle zu behalten)', 'Passwort (Bestätigen)', 'Passwort bestätigen', 'Vorname', 'Vorname eingeben', 'Bevorzugte Sprache', 'Änderungen speichern']
}

def getlanguage():
    if current_user.is_authenticated:
        if current_user.language == 'en':
            language = translations['English']
        elif current_user.language == 'es':
            language = translations['Spanish']
        elif current_user.language == 'fr':
            language = translations['French']
        elif current_user.language == 'pt':
            language = translations['Portuguese']
        elif current_user.language == 'it':
            language = translations['Italian']
        elif current_user.language == 'de':
            language = translations['German']
    else:
        language = translations['English']
            
    return language
            
    
@auth.route('/login', methods=['GET', 'POST'])
def login():
    language = getlanguage()
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash(('Logged in successfully!'), category='success')
                return redirect(url_for('views.home'))
            else:
                flash(('Incorrect email or password, try again.'), category='error')
        else:
            flash(('Incorrect email or password, try again.'), category='error')
    
    return render_template("auth/login.html", user=current_user, language = language)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def signUp():
    language = getlanguage()
    
    email = ""
    first_name = ""
    password1 = ""
    password2 = ""
    
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['firstName']
        password1 = request.form['password1']
        password2 = request.form['password2']
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash(('Email already exists.'), category='error')
        elif not is_valid_email(email):
            flash(('Invalid email address.'), category='error')
        elif first_name == "":
            flash(('First Name cannot be empty.'), category='error')
        elif password1 != password2:
            flash(('Passwords don\'t match.'), category='error')
        elif not is_valid_password(password1):
            flash(('Password must be at least 8 characters long and contain both letters and numbers.'), category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash(('Account created!'), category='success')
            
            return redirect(url_for('views.home'))
            
    return render_template("auth/signup.html", user=current_user, email=email, first_name=first_name, language = language)

@auth.route('/configureuser', methods=['GET', 'POST'])
@login_required
def configureUser():
    language = getlanguage()
    
    if request.method == 'POST':
        email = request.form.get('email')
        password1 = request.form.get('password')
        password2 = request.form.get('password2')
        first_name = request.form.get('first_name')
        lan = request.form.get('language')

        if not is_valid_email(email):
            flash((language[2]), category='error')
            return redirect(url_for('auth.configureUser'))
        if User.query.filter_by(email=email).first() and email != current_user.email:
            flash((language[3]), category='error')
            return redirect(url_for('auth.configureUser'))
        if password1 != password2:
            flash((language[4]), category='error')
            return redirect(url_for('auth.configureUser'))
        if password1 and not is_valid_password(password1):
            flash((language[5]), category='error')
            return redirect(url_for('auth.configureUser'))
        if not first_name:
            flash((language[6]), category='error')
            return redirect(url_for('auth.configureUser'))
        if lan not in ['en', 'es', 'fr', 'pt', 'it', 'de']:
            flash((language[7]), category='error')
            return redirect(url_for('auth.configureUser'))

        user = User.query.get(current_user.id)
        user.email = email
        if password1: 
            user.password = generate_password_hash(password1, method='pbkdf2:sha256')
        user.first_name = first_name
        user.language = lan

        db.session.commit()
        
        language = getlanguage()

        flash((language[8]), category='success')

        return redirect(url_for('views.home'))
    
    return render_template("auth/configureuser.html", user=current_user, language=language)

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True



