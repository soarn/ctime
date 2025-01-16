from flask_wtf import FlaskForm
from wtforms import DateField, StringField, IntegerField, HiddenField, SubmitField, PasswordField, EmailField, BooleanField, FloatField, SelectField, TimeField
from wtforms.validators import DataRequired, NumberRange, Email, Length, Optional


# WEB: LOGIN FORM
class LoginForm(FlaskForm):
    username = StringField  ('Username'   , validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Password'   , validators=[DataRequired()]                )
    remember = BooleanField('Remember Me')
    submit   = SubmitField  ('Login'                                                   )

# WEB: REGISTER FORM
class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name  = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    username   = StringField('Username', validators=[DataRequired(), Length(max=80)])
    email      = EmailField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password   = PasswordField('Password', validators=[DataRequired()])
    submit     = SubmitField('Register')

# # PROFILE: UPDATE FORM
# class UpdateProfileForm(FlaskForm):
#     first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)]          )
#     last_name  = StringField('Last Name' , validators=[DataRequired(), Length(max=50)]          )
#     email      = StringField('Email'     , validators=[DataRequired(), Email(), Length(max=120)])
#     password   = PasswordField('Password', validators=[Optional(), Length(min=8, max=80)]       )
#     submit     = SubmitField('Update'                                                           )

# DASHBOARD: WEEKLY SCHEDULE FORM
class WeeklyScheduleForm(FlaskForm):
    day_of_week = HiddenField('Day of Week', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[Optional()])
    end_time = TimeField('End Time', validators=[Optional()])
    is_virtual = BooleanField('Virtual')
    is_unavailable = BooleanField('Unavailable')
    
    def validate(self):
        if not super().validate():
            return False
        if self.start_time.data and self.end_time.data:
            if self.start_time.data >= self.end_time.data:
                self.end_time.errors.append('End time must be after start time')
                return False
        return True

# DASHBOARD: REQUEST TIME OFF FORM
class TimeOffRequestForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Request Day Off')

# ADMIN: APPROVE/REJECT TIME OFF FORM
class ApproveRejectForm(FlaskForm):
    request_id = HiddenField('Request ID', validators=[DataRequired()])
    action = HiddenField('Action', validators=[DataRequired()])  # 'approve' or 'reject'

class AdminWeeklyScheduleForm(FlaskForm):
    day_of_week = HiddenField("Day of Week", validators=[DataRequired()])
    start_time = TimeField("Start Time", validators=[Optional()])
    end_time = TimeField("End Time", validators=[Optional()])
    is_virtual = BooleanField("Virtual")
    is_unavailable = BooleanField("Unavailable")
    submit = SubmitField("Save Schedule")