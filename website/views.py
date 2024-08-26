from flask import Blueprint, Response, flash, render_template, request, session, url_for, send_file
from website.connections.openai_connection import OpenAIConnection
from website.connections.azure_conection import AzureConnection
import os
from . import db
from .models import Post
from flask_login import current_user

views = Blueprint('views', __name__)

translations = {
    'English': ['New Conversation', 'Configuration', 'Welcome to AI for Accessibility', 'Conversation', 'Type your answer here...', 'Send', 'Restart', 'Welcome back ', '! What would you like to express today?', 'Thanks for your time.', 'Type your comment here...', 'Publish', 'Latest News on Speech Disorders', 'Recent Advances in Understanding Speech Disorders', 'A study published in Nature sheds light on new findings related to speech disorders.', 'Samsung’s New Impulse App Uses AI to Help People with Speech Disorders', 'Samsung has introduced a new app that uses AI to assist people with speech disorders.', 'Psychological Perspectives on Speech Disorders', 'Explore the psychological impact of speech disorders and new therapeutic approaches.', 'Read more'],
    'Spanish': ['Nueva Conversación', 'Configuración', 'Bienvenido a AI for Accessibility', 'Conversación', 'Escribe tu respuesta aquí...', 'Enviar', 'Reiniciar', 'Bienvenido de nuevo ', '! ¿Qué te gustaría expresar hoy?', 'Gracias por tu tiempo.', 'Escribe tu comentario aquí...', 'Publicar', 'Últimas Noticias sobre Trastornos del Habla', 'Avances Recientes en la Comprensión de Trastornos del Habla', 'Un estudio publicado en Nature arroja luz sobre nuevos hallazgos relacionados con los trastornos del habla.', 'La Nueva App Impulse de Samsung Utiliza IA para Ayudar a las Personas con Trastornos del Habla', 'Samsung ha introducido una nueva aplicación que utiliza IA para ayudar a las personas con trastornos del habla.', 'Perspectivas Psicológicas sobre los Trastornos del Habla', 'Explora el impacto psicológico de los trastornos del habla y nuevos enfoques terapéuticos.', 'Leer más'],
    'French': ['Nouvelle Conversation', 'Configuration', 'Bienvenue à AI for Accessibility', 'Conversation', 'Tapez votre réponse ici...', 'Envoyer', 'Redémarrer', 'Bon retour ', '! Que souhaitez-vous exprimer aujourd’hui ?', 'Merci pour votre temps.', 'Tapez votre commentaire ici...', 'Publier', 'Dernières Nouvelles sur les Troubles de la Parole', 'Progrès Récents dans la Compréhension des Troubles de la Parole', 'Une étude publiée dans Nature éclaire de nouvelles découvertes liées aux troubles de la parole.', 'La Nouvelle Application Impulse de Samsung Utilise l’IA pour Aider les Personnes avec des Troubles de la Parole', 'Samsung a introduit une nouvelle application qui utilise l’IA pour aider les personnes ayant des troubles de la parole.', 'Perspectives Psychologiques sur les Troubles de la Parole', 'Explorez l’impact psychologique des troubles de la parole et de nouvelles approches thérapeutiques.', 'Lire plus'],
    'Portuguese': ['Nova Conversa', 'Configuração', 'Bem-vindo ao AI for Accessibility', 'Conversa', 'Digite sua resposta aqui...', 'Enviar', 'Reiniciar', 'Bem-vindo de volta ', '! O que você gostaria de expressar hoje?', 'Obrigado pelo seu tempo.', 'Digite seu comentário aqui...', 'Publicar', 'Últimas Notícias sobre Transtornos da Fala', 'Avanços Recentes na Compreensão dos Transtornos da Fala', 'Um estudo publicado na Nature lança luz sobre novas descobertas relacionadas aos transtornos da fala.', 'O Novo App Impulse da Samsung Usa IA para Ajudar Pessoas com Transtornos da Fala', 'A Samsung introduziu um novo aplicativo que usa IA para ajudar pessoas com transtornos da fala.', 'Perspectivas Psicológicas sobre Transtornos da Fala', 'Explore o impacto psicológico dos transtornos da fala e novas abordagens terapêuticas.', 'Leia mais'],
    'Italian': ['Nuova Conversazione', 'Configurazione', 'Benvenuto in AI for Accessibility', 'Conversazione', 'Scrivi la tua risposta qui...', 'Invia', 'Ricomincia', 'Bentornato ', '! Cosa vorresti esprimere oggi?', 'Grazie per il tuo tempo.', 'Scrivi il tuo commento qui...', 'Pubblica', 'Ultime Notizie sui Disturbi del Linguaggio', 'Progressi Recenti nella Comprensione dei Disturbi del Linguaggio', 'Uno studio pubblicato su Nature fa luce su nuove scoperte relative ai disturbi del linguaggio.', 'La Nuova App Impulse di Samsung Utilizza l’IA per Aiutare le Persone con Disturbi del Linguaggio', 'Samsung ha introdotto una nuova app che utilizza l’IA per aiutare le persone con disturbi del linguaggio.', 'Prospettive Psicologiche sui Disturbi del Linguaggio', 'Esplora l’impatto psicologico dei disturbi del linguaggio e nuovi approcci terapeutici.', 'Leggi di più'],
    'German': ['Neues Gespräch', 'Konfiguration', 'Willkommen bei AI for Accessibility', 'Gespräch', 'Geben Sie hier Ihre Antwort ein...', 'Senden', 'Neustart', 'Willkommen zurück ', '! Was möchten Sie heute ausdrücken?', 'Danke für Ihre Zeit.', 'Geben Sie hier Ihren Kommentar ein...', 'Veröffentlichen', 'Neueste Nachrichten zu Sprachstörungen', 'Jüngste Fortschritte im Verständnis von Sprachstörungen', 'Eine in Nature veröffentlichte Studie beleuchtet neue Erkenntnisse zu Sprachstörungen.', 'Samsungs neue Impulse-App verwendet KI, um Menschen mit Sprachstörungen zu helfen', 'Samsung hat eine neue App eingeführt, die KI verwendet, um Menschen mit Sprachstörungen zu unterstützen.', 'Psychologische Perspektiven auf Sprachstörungen', 'Erkunden Sie die psychologischen Auswirkungen von Sprachstörungen und neue therapeutische Ansätze.', 'Mehr lesen']
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

@views.route('/')
def home():
    language = getlanguage()
    
    return render_template("home.html", user=current_user, language=language)

@views.route('/newconversation', methods=['GET', 'POST'])
def new_conversation():
    language = getlanguage()
    
    if 'conversation' not in session:
        session['conversation'] = {}
        session['json'], session['final_json'] = OpenAIConnection.initialize(language=language)
        session['question'] = ("{language1}{first_name}{language2}").format(language1=language[7], first_name=current_user.first_name, language2=language[8])

    conversation = session['conversation']
    json = session['json']
    final_json = session['final_json']
    question = session['question']

    if request.method == 'POST':
        answer = request.form['answer']

        conversation, json, final_json, question = OpenAIConnection.conversation(conversation, json, final_json, question, answer)

        session['conversation'] = conversation
        session['json'] = json
        session['final_json'] = final_json
        session['question'] = question
        
        flag = False
        if question == language[9] and not flag:
            flag = True
            paragraph = OpenAIConnection.create_paragraph(final_json)
            audio_data = AzureConnection.text_to_speech(paragraph)
            if audio_data:
                audio_path = os.path.join('static', 'audio', 'output.wav')
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                with open(audio_path, 'wb') as audio_file:
                    audio_file.write(audio_data)
                return render_template('conversation/newconversation.html', user=current_user, conversation=conversation, question=question, audio_url=url_for('static', filename='audio/output.wav'), language=language)

        return render_template('conversation/newconversation.html', user=current_user, conversation=conversation, question=question, language=language)
    
    else:
        session.pop('conversation', None)
        session.pop('json', None)
        session.pop('final_json', None)
        session.pop('question', None)
        question = ("{language5}{first_name}{language6}").format(language5=language[7], first_name=current_user.first_name, language6=language[8])
        
        return render_template('conversation/newconversation.html', user=current_user, conversation={}, question=question, language=language)

@views.route('/forum', methods=['GET', 'POST'])
def forum():
    language = getlanguage()

    if request.method == 'POST':
        post = request.form.get('post')

        if len(post) < 1:
            flash('Comment is too short.', category='error') 
        else:
            new_post = Post(data=post, user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            flash('Comment Posted!', category='success')

    posts = Post.query.order_by(Post.date.desc()).all()

    return render_template('views/forum.html', user=current_user, language=language, posts=posts)


