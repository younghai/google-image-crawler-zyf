from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, IntegerField, FloatField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from .models.user import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

from pywebpush import generate_vapid_keys

class VAPIDKeyForm(FlaskForm):
    generate_new = BooleanField('Generate New VAPID Keys')
    public_key = StringField('VAPID Public Key', validators=[Length(max=200)])
    private_key = StringField('VAPID Private Key', validators=[Length(max=200)])
    claims_email = StringField('Contact Email for VAPID Claims (e.g., mailto:admin@example.com)', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Save VAPID Configuration')

    # Optionally, validate that if not generating new, keys are provided
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        if not self.generate_new.data:
            if not self.public_key.data or not self.private_key.data:
                self.public_key.errors.append('Public and Private keys are required if not generating new ones.')
                return False
        if not self.claims_email.data:
             self.claims_email.errors.append('VAPID Claims email is required.')
             return False
        return True


class HelloBarForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired(), Length(max=100)])
    message_text = StringField('Message Text', validators=[DataRequired(), Length(max=255)])
    cta_text = StringField('CTA Button Text', validators=[Length(max=50)])
    cta_link = StringField('CTA Button Link (URL)', validators=[Length(max=2048)])
    background_color = StringField('Background Color (hex, e.g., #FF0000)', default='#007bff', validators=[Length(max=7)])
    text_color = StringField('Text Color (hex, e.g., #FFFFFF)', default='#FFFFFF', validators=[Length(max=7)])
    position = SelectField('Position', choices=[('top', 'Top of Page'), ('bottom', 'Bottom of Page')], default='top')
    is_active = BooleanField('Activate this Hello Bar', default=True)
    submit = SubmitField('Save Hello Bar')

    def validate_background_color(self, field):
        if field.data and not (field.data.startswith('#') and len(field.data) in [4, 7]):
            raise ValidationError('Invalid hex color format for background (e.g., #RGB or #RRGGBB).')

    def validate_text_color(self, field):
        if field.data and not (field.data.startswith('#') and len(field.data) in [4, 7]):
            raise ValidationError('Invalid hex color format for text (e.g., #RGB or #RRGGBB).')


class BannerForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired(), Length(max=100)])
    image_url = StringField('Image URL', validators=[DataRequired(), Length(max=2048)]) # Consider URL validator
    link_url = StringField('Link URL (on banner click)', validators=[DataRequired(), Length(max=2048)]) # Consider URL validator
    # For simplicity, let's start with some predefined positions/types.
    # 'inline' would mean user places a div with an ID. 'fixed_bottom_right' is an example.
    position_type = SelectField('Banner Type/Position',
                                choices=[
                                    ('inline_replace', 'Inline (Replaces a div with specific ID)'),
                                    ('fixed_bottom_right', 'Fixed - Bottom Right'),
                                    ('fixed_bottom_left', 'Fixed - Bottom Left'),
                                    ('fixed_top_right', 'Fixed - Top Right'),
                                    ('fixed_top_left', 'Fixed - Top Left')
                                ],
                                default='inline_replace')
    # If inline_replace, user needs to specify the target div ID on their site.
    target_div_id = StringField('Target DIV ID (for Inline type)', validators=[Length(max=100)])
    width = StringField('Width (e.g., 300px or 100%)', default='300px', validators=[Length(max=20)])
    height = StringField('Height (e.g., 250px or auto)', default='250px', validators=[Length(max=20)])
    is_active = BooleanField('Activate this Banner', default=True)
    submit = SubmitField('Save Banner Campaign')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        if self.position_type.data == 'inline_replace' and not self.target_div_id.data:
            self.target_div_id.errors.append('Target DIV ID is required for Inline banner type.')
            return False
        return True


class PopupForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired(), Length(max=100)])
    popup_type = SelectField('Popup Content Type',
                             choices=[
                                 ('custom_html', 'Custom HTML'),
                                 ('youtube_video', 'YouTube Video')
                             ],
                             default='custom_html')
    title = StringField('Popup Title (Optional)', validators=[Length(max=100)])

    # Custom HTML Fields
    custom_html_content = TextAreaField('Custom HTML Content (use with "Custom HTML" type)')

    # YouTube Fields
    youtube_video_id = StringField('YouTube Video ID (use with "YouTube Video" type)',
                                   validators=[Length(max=20)],
                                   description="E.g., dQw4w9WgXcQ from https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    # Trigger Settings
    trigger_type = SelectField('Trigger',
                               choices=[
                                   ('on_load', 'On Page Load'),
                                   # ('on_exit_intent', 'On Exit Intent (Advanced)'),
                                   # ('on_scroll', 'After Scrolling X% (Advanced)'),
                               ],
                               default='on_load')
    trigger_delay = IntegerField('Delay (seconds, for On Page Load)', default=3, validators=[DataRequired()]) # NumberRange(min=0) would be good

    # Display Frequency
    display_frequency = SelectField('Display Frequency',
                                    choices=[
                                        ('every_time', 'Every Time Page Loads'),
                                        ('once_per_session', 'Once Per Browser Session'),
                                        # ('once_ever', 'Once Ever (per browser)')
                                    ],
                                    default='once_per_session')

    # Appearance
    width = StringField('Popup Width (e.g., 600px or 80%)', default='600px', validators=[Length(max=20)])
    # height = StringField('Popup Height (e.g., 400px or auto)', default='auto', validators=[Length(max=20)]) # Auto height usually better for popups
    overlay_color = StringField('Overlay Color (e.g., rgba(0,0,0,0.5))', default='rgba(0,0,0,0.5)', validators=[Length(max=30)])

    is_active = BooleanField('Activate this Popup', default=True)
    submit = SubmitField('Save Popup Campaign')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        if self.popup_type.data == 'custom_html' and not self.custom_html_content.data:
            self.custom_html_content.errors.append('Custom HTML content is required for this popup type.')
            return False
        if self.popup_type.data == 'youtube_video' and not self.youtube_video_id.data:
            self.youtube_video_id.errors.append('YouTube Video ID is required for this popup type.')
            return False

        if self.trigger_delay.data is None or self.trigger_delay.data < 0:
            self.trigger_delay.errors.append('Trigger delay must be a non-negative number.')
            return False

        return True


# Imports for CouponForm are covered by the main imports at the top of the file.
# from .models.coupon import Coupon # This is fine if it's the first time Coupon is imported.
# from flask import request # This is fine if it's the first time request is imported.
# We need to ensure .models.coupon and flask.request are imported if not already.
# The main imports at the top handle wtforms and wtforms.validators.

from .models.coupon import Coupon # Keep this, specific to this form block
from flask import request # Keep this, specific to this form block

class CouponForm(FlaskForm):
    code = StringField('Coupon Code',
                       validators=[DataRequired(), Length(min=3, max=50)],
                       description="Enter a unique code (e.g., SUMMER25) or leave blank to auto-generate.")
    description = StringField('Description (Optional)', validators=[Optional(), Length(max=255)])
    discount_type = SelectField('Discount Type',
                                choices=[('percentage', 'Percentage Off'), ('fixed_amount', 'Fixed Amount Off')],
                                default='percentage', validators=[DataRequired()])
    discount_value = FloatField('Discount Value', validators=[DataRequired(), NumberRange(min=0.01)])

    valid_from = DateTimeField('Valid From (Optional, YYYY-MM-DD HH:MM:SS)',
                               format='%Y-%m-%d %H:%M:%S', validators=[Optional()])
    valid_to = DateTimeField('Valid To (Optional, YYYY-MM-DD HH:MM:SS)',
                             format='%Y-%m-%d %H:%M:%S', validators=[Optional()])

    max_uses = IntegerField('Max Uses (Optional, 0 for unlimited)', validators=[Optional(), NumberRange(min=0)])
    # uses_count will be managed by the system

    is_active = BooleanField('Activate this Coupon', default=True)
    generate_code_checkbox = BooleanField('Auto-generate Code (if Code field is blank)', default=False)
    submit = SubmitField('Save Coupon')

    def validate_code(self, field):
        # If we are editing (instance is passed), allow current code.
        # For new coupons, or if code is changed during edit, check uniqueness.
        coupon_id = request.form.get('coupon_id_hidden') # Hidden field to pass coupon ID during edit
        query = Coupon.query.filter_by(code=field.data)
        if coupon_id: # Editing existing coupon
            # Ensure coupon_id is an integer for comparison if your DB expects it
            try:
                coupon_id = int(coupon_id)
                existing_coupon = query.filter(Coupon.id != coupon_id).first()
            except ValueError: # Handle case where coupon_id might not be a valid int string
                existing_coupon = query.first() # Fallback or raise error
        else: # Creating new coupon
            existing_coupon = query.first()

        if existing_coupon:
            raise ValidationError(f'Coupon code "{field.data}" already exists. Please choose a different one.')

    def validate_valid_to(self, field):
        if field.data and self.valid_from.data and field.data < self.valid_from.data:
            raise ValidationError('End date cannot be earlier than start date.')


# Template types can be dynamically populated or predefined.
# For now, let's predefine some common ones.
PREDEFINED_TEMPLATE_TYPES = [
    ('popup_custom_html', 'Popup - Custom HTML Content'),
    ('email_body_html', 'Email - HTML Body (Example)'),
    ('hellobar_message_text', 'HelloBar - Message Text (Example)'),
    # Add more as features are developed
]

class TemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired(), Length(max=100)])
    description = StringField('Description (Optional)', validators=[Optional(), Length(max=255)])
    template_type = SelectField('Template Type', choices=PREDEFINED_TEMPLATE_TYPES, validators=[DataRequired()])
    content = TextAreaField('Template Content', validators=[DataRequired()], render_kw={"rows": 10, "cols": 80})
    submit = SubmitField('Save Template')

    def validate_name(self, field):
        # Check if template name is unique for the current user and type
        # Ensure flask.request and current_user are available in the context this form is used
        # This validation might be better placed in the route if current_user is not easily accessible here
        # For now, assuming it can be accessed or this part will be adjusted in route.
        from flask_login import current_user # Local import for validation context
        from flask import request # Local import for validation context
        from .models.template import Template # Local import for validation context

        template_id_hidden = request.form.get('template_id_hidden')
        query = Template.query.filter_by(user_id=current_user.id, name=field.data, template_type=self.template_type.data)
        if template_id_hidden:
            try:
                query = query.filter(Template.id != int(template_id_hidden))
            except ValueError:
                # Handle case where template_id_hidden is not a valid int, though it should be
                pass

        existing_template = query.first()
        if existing_template:
            raise ValidationError(f'A template with this name and type already exists.')
