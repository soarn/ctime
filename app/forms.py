from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, HiddenField, PasswordField, StringField, SubmitField, TimeField
from wtforms.validators import DataRequired, NumberRange, Email, Length, Optional


# WEB: LOGIN FORM
class LoginForm(FlaskForm):
    username = StringField  ('Username'   , validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Password'   , validators=[DataRequired()]                )
    remember = BooleanField ('Remember Me'                                             )
    submit   = SubmitField  ('Login'                                                   )

# WEB: REGISTER FORM
class RegisterForm(FlaskForm):
    first_name = StringField  ('First Name', validators=[DataRequired(), Length(max=50)]          )
    last_name  = StringField  ('Last Name' , validators=[DataRequired(), Length(max=50)]          )
    username   = StringField  ('Username'  , validators=[DataRequired(), Length(max=80)]          )
    email      = StringField  ('Email'     , validators=[DataRequired(), Email(), Length(max=120)])
    password   = PasswordField('Password'  , validators=[DataRequired(), Length(min=8, max=80)]   )
    submit     = SubmitField  ('Register'                                                         )

# # PROFILE: UPDATE FORM
# class UpdateProfileForm(FlaskForm):
#     first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)]          )
#     last_name  = StringField('Last Name' , validators=[DataRequired(), Length(max=50)]          )
#     email      = StringField('Email'     , validators=[DataRequired(), Email(), Length(max=120)])
#     password   = PasswordField('Password', validators=[Optional(), Length(min=8, max=80)]       )
#     submit     = SubmitField('Update'                                                           )

# DASHBOARD: WEEKLY SCHEDULE FORM
class WeeklyScheduleForm(FlaskForm):
    day_of_week = StringField('Day of Week', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[Optional()])
    end_time = TimeField('End Time', validators=[Optional()])
    is_virtual = BooleanField('Virtual')
    is_unavailable = BooleanField('Unavailable')

class TimeOffRequestForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Request Day Off')

class ApproveRejectForm(FlaskForm):
    request_id = HiddenField('Request ID', validators=[DataRequired()])
    action = HiddenField('Action', validators=[DataRequired()])  # 'approve' or 'reject'

class AdminScheduleForm(FlaskForm):
    user_id = HiddenField('User ID', validators=[DataRequired()])
    schedules = HiddenField('Schedules', validators=[Optional()])  # JSON-encoded schedule data
    submit = SubmitField('Save Changes')