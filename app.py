import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv 

# Cargar las variables de entorno
load_dotenv()

# Crear instancia
app = Flask(__name__)

# Configuración de la base de datos PostgreSQL
db_uri = os.getenv('DATABASE_URL', '')
if db_uri.startswith('postgres://'):
    db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo Categoría
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

# Modelo Post
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship('Category', backref=db.backref('posts', lazy=True))

# Crear las tablas automáticamente si no existen e insertar categorías de prueba
with app.app_context():
    db.create_all()
    if not Category.query.first():
        db.session.add_all([
            Category(name="Tecnología"),
            Category(name="Deportes"),
            Category(name="General")
        ])
        db.session.commit()

# Ruta para ver todos los posts
@app.route('/')
def index():
    posts = Post.query.all()
    categories = Category.query.all()
    return render_template('index.html', posts=posts, categories=categories)

# Ruta /post crear un nuevo post
@app.route('/post/new', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = request.form.get('category_id')
        new_post = Post(title=title, content=content, category_id=category_id)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('index'))
    
    # Aquí sigue si es GET
    categories = Category.query.all()
    return render_template('create_post.html', categories=categories)

if __name__ == '__main__':
    app.run(debug=True)