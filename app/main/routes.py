from flask import render_template, request
from app.main import bp
from app.models import Post

@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=5 # Esempio di paginazione
    )
    return render_template('home.html', title='Home', posts=posts)