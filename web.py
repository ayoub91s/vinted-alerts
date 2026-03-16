from flask import Flask, render_template, jsonify, request
import psycopg2
import psycopg2.extras
import os
import requests

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

ALERTES = [
    {"nom": "Rick Owens", "brand_id": 145654},
    {"nom": "Ann Demeulemeester", "brand_id": 51445},
    {"nom": "Isaac Sellam", "brand_id": 393343},
    {"nom": "Mon profil", "user_id": 0},
]

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def get_articles(alerte=None, limit=200):
    try:
        conn = get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if alerte:
            c.execute(
                'SELECT * FROM articles_vus WHERE nom_alerte=%s ORDER BY trouve_le DESC LIMIT %s',
                (alerte, limit)
            )
        else:
            c.execute(
                '''SELECT DISTINCT ON (vinted_id) vinted_id, nom_alerte, titre, prix, photo_url, trouve_le
                   FROM articles_vus
                   ORDER BY vinted_id, trouve_le DESC
                   LIMIT %s''',
                (limit,)
            )
        rows = c.fetchall()
        conn.close()
        result = []
        for r in rows:
            d = dict(r)
            if d.get('trouve_le'):
                d['trouve_le'] = d['trouve_le'].isoformat()
            result.append(d)
        return result
    except Exception as e:
        print(f"Erreur get_articles: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html', alertes=ALERTES)

@app.route('/api/articles')
def api_articles():
    alerte = request.args.get('alerte')
    articles = get_articles(alerte)
    # Trier par trouve_le desc
    articles.sort(key=lambda x: x.get('trouve_le', ''), reverse=True)
    return jsonify(articles)

@app.route('/api/acheter/<item_id>', methods=['POST'])
def api_acheter(item_id):
    try:
        from app import acheter_article
        succes, message = acheter_article(item_id)
        return jsonify({"succes": succes, "message": message})
    except Exception as e:
        return jsonify({"succes": False, "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
