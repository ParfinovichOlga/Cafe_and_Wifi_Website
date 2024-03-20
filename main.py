from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap4
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, URL


app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
db = SQLAlchemy()
db.init_app(app)
Bootstrap4(app)


# Form for adding a new cafe
class MyForm(FlaskForm):
    name = StringField('Cafe Name', validators=[DataRequired()])
    map_url = StringField('Map URL', validators=[DataRequired(), URL()])
    img_url = StringField('Image URL', validators=[DataRequired(), URL()])
    loc = StringField('Location', validators=[DataRequired()])
    seats = StringField('Seats', validators=[DataRequired()])
    price = StringField('Coffee price, £', validators=[DataRequired()])
    sockets = BooleanField('Has sockets', default=False)
    toilet = BooleanField('Has toilet',  default=False)
    wifi = BooleanField('Has WiFi',  default=False)
    calls = BooleanField('Can take calls',  default=False)
    submit = SubmitField('Submit Cafe')


# Form for editing coffee price
class EditForm(FlaskForm):
    price = StringField('Coffee price', validators=[DataRequired()])
    submit = SubmitField('Submit Changes')


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.String(250), nullable=False)
    has_wifi = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.String(250), nullable=False)
    can_take_calls = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


with app.app_context():
    db.create_all()


API_KEY = "TopSecretAPIKey"


@app.route("/")
def home():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    return render_template("index.html", cafes=all_cafes)


@app.route("/search", methods=['GET', 'POST'])
def search_cafe():
    query_location = request.form["location"].title()
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    all_cafes = result.scalars().all()
    return render_template('index.html', cafes=all_cafes)


@app.route("/add", methods=["POST", "GET"])
def post_new_cafe():
    form = MyForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.loc.data,
            has_sockets=form.sockets.data,
            has_toilet=form.toilet.data,
            has_wifi=form.wifi.data,
            can_take_calls=form.calls.data,
            seats=form.seats.data,
            coffee_price=f"£{form.price.data}",
        )
        if db.session.execute(db.select(Cafe).where(Cafe.name == form.name.data)).scalar():
            flash('Cafe with such name is already exist')
            return redirect(url_for('post_new_cafe'))
        else:
            db.session.add(new_cafe)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('add-cafe.html', form=form)


@app.route("/update-price/<cafe_id>", methods=["GET", "POST"])
def update_price(cafe_id):
    cafe_to_update = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    edit_form = EditForm(
        price=cafe_to_update.coffee_price.split('£')[1]
    )
    if cafe_to_update:
        if edit_form.validate_on_submit():
            new_price = edit_form.price.data
            cafe_to_update.coffee_price = f"£{new_price}"
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('add-cafe.html', cafe=cafe_to_update, form=edit_form, is_edit=True)


@app.route("/report-closed/<cafe_id>")
def delete_cafe(cafe_id):
    cafe_to_delete = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    if cafe_to_delete:
        db.session.delete(cafe_to_delete)
        db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
