from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.template import Template # The new Template model
from app.forms import TemplateForm, PREDEFINED_TEMPLATE_TYPES # Import form and types

templates_bp = Blueprint('templates_mgmt', __name__) # Renamed blueprint

@templates_bp.route('/list')
@login_required
def list_templates():
    templates = Template.query.filter_by(owner=current_user).order_by(Template.template_type, Template.name).all()
    return render_template('templates_mgmt/list_templates.html', title='My Content Templates', templates=templates)

@templates_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_template():
    form = TemplateForm()
    # form.template_type.choices = PREDEFINED_TEMPLATE_TYPES # Choices are set in form definition
    if form.validate_on_submit():
        new_template = Template(
            name=form.name.data,
            description=form.description.data,
            template_type=form.template_type.data,
            content=form.content.data,
            owner=current_user
        )
        db.session.add(new_template)
        db.session.commit()
        flash(f'Template "{new_template.name}" created successfully!', 'success')
        return redirect(url_for('templates_mgmt.list_templates'))
    return render_template('templates_mgmt/create_edit_template.html', title='Create New Template', form=form, legend='New Template')

@templates_bp.route('/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_template(template_id):
    template = Template.query.get_or_404(template_id)
    if template.owner != current_user:
        flash('You do not have permission to edit this template.', 'danger')
        return redirect(url_for('templates_mgmt.list_templates'))

    form = TemplateForm(obj=template)
    # form.template_type.choices = PREDEFINED_TEMPLATE_TYPES
    if form.validate_on_submit():
        template.name = form.name.data
        template.description = form.description.data
        # template.template_type = form.template_type.data # Type is not changed after creation as per template
        template.content = form.content.data
        db.session.commit()
        flash(f'Template "{template.name}" updated successfully!', 'success')
        return redirect(url_for('templates_mgmt.list_templates'))

    return render_template('templates_mgmt/create_edit_template.html', title='Edit Template', form=form, legend=f'Edit {template.name}', template_id_hidden=template.id)

@templates_bp.route('/<int:template_id>/delete', methods=['POST'])
@login_required
def delete_template(template_id):
    template = Template.query.get_or_404(template_id)
    if template.owner != current_user:
        flash('You do not have permission to delete this template.', 'danger')
        return redirect(url_for('templates_mgmt.list_templates'))

    template_name = template.name # Get name before deleting
    db.session.delete(template)
    db.session.commit()
    flash(f'Template "{template_name}" deleted successfully!', 'success')
    return redirect(url_for('templates_mgmt.list_templates'))

# Route to get template content (e.g., for AJAX call when selecting a template in campaign form)
@templates_bp.route('/get/<int:template_id>/content')
@login_required
def get_template_content(template_id):
    template = Template.query.get_or_404(template_id)
    if template.owner != current_user:
        return jsonify(error="Permission denied"), 403
    return jsonify(name=template.name, type=template.template_type, content=template.content)

EOF
