from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class PropertyDetailsForm(FlaskForm):
  property_name = StringField('Property Name', validators=[DataRequired(message="Property name field required"), Length(max=100)])
  region = StringField('Region', validators=[DataRequired(message="Region field required"), Length(max=50)])
  district = StringField('District', validators=[DataRequired(message="District field required"), Length(max=50)])
  town = StringField('Town', validators=[DataRequired(message="Town field required"), Length(max=50)])
  house_number = StringField('House Number/Street/Apartment No', validators=[DataRequired(message="House No field required"), Length(max=100)])

class AmenitiesForm(FlaskForm):
  name = StringField('Amenity', validators=[DataRequired(message="Amenities field required"), Length(max=100)])

class ImagesForm(FlaskForm):
  images = FileField('Property Images', validators=[
    FileRequired(),
    FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only!')
  ])
  submit = SubmitField('Submit Listing')
