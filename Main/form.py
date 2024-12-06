from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import Length, Email, DataRequired

class UnitEnquiryForm(FlaskForm):
  first_name = StringField(label="First Name", validators=[DataRequired(message="First Name field required")])
  last_name = StringField(label="Last Name", validators=[DataRequired(message="Last Name field required")])
  email_address = StringField(label="Email Address", validators=[Email(), DataRequired(message="Email Address field required")])
  phone_number = StringField(label="Phone number", validators=[Length(min=10, max=10, message="Invalid Phone Number"), DataRequired(message="Phone Number field required")])
  message = TextAreaField(label="Message", validators=[DataRequired(message="Message field required")])
