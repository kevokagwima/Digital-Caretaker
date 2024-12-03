from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import Length, Email, DataRequired, ValidationError
from Models.extras import Extras

class Extra_signup(FlaskForm):
  first_name = StringField(label="Enter First Name", validators=[DataRequired(Length(min=5, max=80, message="Invalid Name"))])
  last_name = StringField(label="Enter Last Name", validators=[DataRequired(Length(min=5, max=80, message="Invalid Name"))])
  phone_number = StringField(label="Enter Phone Number", validators=[DataRequired(Length(min=10, max=10, message="Invalid Phone Number"))])
  email_address = StringField(label="Email Address", validators=[Email(), DataRequired()])
  age = IntegerField(label="Enter Age", validators=[DataRequired()])
  title = StringField(label="Enter Title", validators=[DataRequired(Length(min=6, max=15, message="Invalid Title"))])
  cost = IntegerField(label="Enter Cost", validators=[DataRequired()])

  def validate_phone_number(self, phone_number_to_validate):
    phone_number = Extras.query.filter_by(phone=phone_number_to_validate.data).first()
    if phone_number:
      raise ValidationError("Phone Number already exists, Please try another one")

  def validate_email_address(self, email_to_validate):
    email = Extras.query.filter_by(email=email_to_validate.data).first()
    if email:
      raise ValidationError("Email Address already exists, Please try another one")

class Admin_login_form(FlaskForm):
  admin_id = StringField(label="Email Address", validators=[DataRequired()])
  password = PasswordField(label="Password", validators=[DataRequired()])
