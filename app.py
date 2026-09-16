import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv 


load_dotenv()


app = Flask(__name__)


db_uri = os.getenv('DATABASE_URL', '')
if db_uri.startswith('postgres://'):
    db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

# Asegurar sslmode=require si se ejecuta en local y no lo incluye
if db_uri and 'sslmode=' not in db_uri and 'localhost' not in db_uri and '127.0.0.1' not in db_uri:
    separator = '&' if '?' in db_uri else '?'
    db_uri = f"{db_uri}{separator}sslmode=require"

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
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    category = db.relationship('Category', backref=db.backref('posts', lazy=True))

# Crear tablas y sembrar datos requeridos por el examen
with app.app_context():
    db.create_all()
    if not Category.query.first():
        categorias_iniciales = [
            Category(id=1, name='Tecnología'),
            Category(id=2, name='Negocios'),
            Category(id=3, name='Entretenimiento'),
            Category(id=4, name='Finanzas'),
            Category(id=5, name='Salud')
        ]
        db.session.add_all(categorias_iniciales)
        db.session.commit()

    if not Post.query.first():
        post_inicial = Post(
            id=1,
            title='Bitcoin alcanza su máximo histórico en 2023',
            content='El Bitcoin ha superado nuevamente las expectativas al alcanzar un nuevo máximo histórico de $45,000 este mes, impulsado por la adopción masiva de criptomonedas en países emergentes y el interés de grandes instituciones financieras. Analistas sugieren que este repunte se debe a la creciente demanda de activos digitales como alternativa a las monedas tradicionales. Sin embargo, expertos advierten sobre la volatilidad del mercado y recomiendan invertir con precaución. Mientras tanto, otras criptomonedas como Ethereum y Solana también han experimentado alzas significativas.',
            category_id=2
        )
        db.session.add(post_inicial)
        db.session.commit()

@app.route('/')
def index():
    posts = Post.query.all()
    categories = Category.query.all()
    return render_template('index.html', posts=posts, categories=categories)

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
    
    categories = Category.query.all()
    return render_template('create_post.html', categories=categories)


@app.route('/post/update/<int:id>', methods=['GET', 'POST'])
def update_post(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.category_id = request.form['category_id']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    return render_template('update_post.html', post=post, categories=categories)


@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post = Post.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)