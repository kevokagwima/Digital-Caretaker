from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, MultipleFileField
from wtforms.validators import DataRequired

class PropertyRegistrationForm(FlaskForm):
  name = StringField(label="Property Name", validators=[DataRequired(message="Property name required")])
  county = StringField(label="County", validators=[DataRequired(message="County name required")])
  city = StringField(label="City/Town", validators=[DataRequired(message="City/town name required")])
  floors = IntegerField(label="Property Floors", validators=[DataRequired(message="Property floors required")])
  total_units = IntegerField(label="Total Property Units", validators=[DataRequired(message="Property name required")])
  property_type = SelectField(label="Property Type", choices=["Apartment"], validators=[DataRequired(message="Property type required")])

class UnitRegistrationForm(FlaskForm):
  name = StringField(label="Unit Name", validators=[DataRequired(message="Unit name required")])
  floor = IntegerField(label="Unit Floor", validators=[DataRequired(message="Unit Floor required")])
  rent_amount = IntegerField(label="Unit Rent", validators=[DataRequired(message="Unit Rent required")])
  living_room_space = IntegerField(label="Living Room Space (SQM)", validators=[DataRequired(message="Living Room Space required")])
  balcony_room_space = IntegerField(label="Balcony Space (SQM)", validators=[DataRequired(message="Balcony Space required")])
  bedrooms = IntegerField(label="No of Bedrooms", validators=[DataRequired(message="Bedrooms required")])
  bathrooms = IntegerField(label="No of Bathrooms", validators=[DataRequired(message="Bathrooms required")])
  unit_type = SelectField(label="Unit Type", choices=["BedSitter", "1 Bedroom", "2 Bedroom", "3 Bedroom", "4 Bedroom", "5 Bedroom",  "Penthouse"], validators=[DataRequired(message="Unit type required")])
  unit_image = MultipleFileField(label="Unit Images", validators=[DataRequired(message="Atleast 1 emage is required")])
