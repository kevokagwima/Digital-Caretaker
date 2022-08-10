from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from models import Landlord

class landlord_form(FlaskForm):
  first_name = StringField(label="First Name", validators=[DataRequired()])
  second_name = StringField(label="Second Name", validators=[DataRequired()])
  last_name = StringField(label="Last Name", validators=[DataRequired()])
  email_address = StringField(label="Email Address", validators=[Email(), DataRequired()])
  phone_number = StringField(label="Phone number",validators=[Length(min=10, max=10, message="Invalid Phone Number"),DataRequired()])
  username = StringField(label="Username",validators=[Length(min=5,max=25,message="Username has to be between 5 and 25 characters long"),DataRequired()])
  password = PasswordField(label="Password",validators=[Length(min=5,message="Password has to be between 5 and 25 characters long",),DataRequired()])
  password1 = PasswordField(label="Confirm Password",validators=[EqualTo("password",message="Passwords do not match"),DataRequired()])

  def validate_phone_number(self, phone_number_to_validate):
    phone_number = Landlord.query.filter_by(phone=phone_number_to_validate.data).first()
    if phone_number:
      raise ValidationError("Phone Number already exists, Please try another one")

  def validate_phone_number(self, phone_number_to_validate):
    phone_number = phone_number_to_validate.data
    if phone_number[0] != str(0):
      raise ValidationError("Invalid phone number. Phone number must begin with 0")
    elif phone_number[1] != str(7) and phone_number[1] != str(1):
      raise ValidationError("Invalid phone number. Phone number must begin with 0 followed by 7 or 1")

  def validate_email_address(self, email_to_validate):
    email = Landlord.query.filter_by(email=email_to_validate.data).first()
    if email:
      raise ValidationError("Email Address already exists, Please try another one")

class landlord_login_form(FlaskForm):
  landlord_id = IntegerField(label="Enter Landlord ID", validators=[DataRequired()])
  password = PasswordField(label="Enter Password", validators=[DataRequired()])
