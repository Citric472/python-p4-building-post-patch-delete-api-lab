from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(jsonify(bakeries), 200)

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return make_response(jsonify({'error': 'Bakery not found.'}), 404)

    data = request.form.to_dict()
    for key, value in data.items():
        setattr(bakery, key, value)

    db.session.commit()
    return make_response(jsonify(bakery.to_dict()), 200)

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    data = request.form.to_dict()

    # Validate required fields
    if 'name' not in data or 'price' not in data or 'bakery_id' not in data:
        return make_response(jsonify({'error': 'Missing required fields: name, price, bakery_id'}), 400)

    baked_good = BakedGood(**data)
    db.session.add(baked_good)
    db.session.commit()

    return make_response(jsonify(baked_good.to_dict()), 201)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)
    if not baked_good:
        return make_response(jsonify({'error': 'Baked good not found.'}), 404)

    db.session.delete(baked_good)
    db.session.commit()
    return make_response(jsonify({'message': 'Baked good deleted successfully.'}), 200)

@app.route('/bakeries/<int:id>', methods=['GET'])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    if not bakery:
        return make_response(jsonify({'error': 'Bakery not found.'}), 404)

    return make_response(jsonify(bakery.to_dict()), 200)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [bg.to_dict() for bg in baked_goods_by_price]
    return make_response(jsonify(baked_goods_by_price_serialized), 200)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    if not most_expensive:
        return make_response(jsonify({'error': 'No baked goods found.'}), 404)

    return make_response(jsonify(most_expensive.to_dict()), 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
