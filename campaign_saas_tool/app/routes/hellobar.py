from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.campaign import Campaign # Using the generic Campaign model
from app.forms import HelloBarForm # Ensure this is imported
import json # For storing settings as JSON

hellobar_bp = Blueprint('hellobar', __name__)

@hellobar_bp.route('/list')
@login_required
def list_hellobars():
    hellobars = Campaign.query.filter_by(owner=current_user, campaign_type='hello_bar').order_by(Campaign.created_at.desc()).all()
    return render_template('hellobar/list_hellobars.html', title='My Hello Bars', hellobars=hellobars)

@hellobar_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_hellobar():
    form = HelloBarForm()
    if form.validate_on_submit():
        settings = {
            'message_text': form.message_text.data,
            'cta_text': form.cta_text.data,
            'cta_link': form.cta_link.data,
            'background_color': form.background_color.data,
            'text_color': form.text_color.data,
            'position': form.position.data
        }
        hellobar_campaign = Campaign(
            name=form.name.data,
            campaign_type='hello_bar',
            is_active=form.is_active.data,
            owner=current_user,
            settings=json.dumps(settings)
        )
        db.session.add(hellobar_campaign)
        db.session.commit()
        flash('Hello Bar campaign created successfully!', 'success')
        return redirect(url_for('hellobar.list_hellobars'))
    return render_template('hellobar/create_edit_hellobar.html', title='Create Hello Bar', form=form, legend='New Hello Bar')

@hellobar_bp.route('/<int:campaign_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_hellobar(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner != current_user or campaign.campaign_type != 'hello_bar':
        flash('You do not have permission to edit this campaign or it is not a Hello Bar.', 'danger')
        return redirect(url_for('hellobar.list_hellobars'))

    form = HelloBarForm()
    if form.validate_on_submit():
        settings = {
            'message_text': form.message_text.data,
            'cta_text': form.cta_text.data,
            'cta_link': form.cta_link.data,
            'background_color': form.background_color.data,
            'text_color': form.text_color.data,
            'position': form.position.data
        }
        campaign.name = form.name.data
        campaign.is_active = form.is_active.data
        campaign.settings = json.dumps(settings)
        db.session.commit()
        flash('Hello Bar campaign updated successfully!', 'success')
        return redirect(url_for('hellobar.list_hellobars'))
    elif request.method == 'GET':
        settings = json.loads(campaign.settings) if campaign.settings else {}
        form.name.data = campaign.name
        form.is_active.data = campaign.is_active
        form.message_text.data = settings.get('message_text')
        form.cta_text.data = settings.get('cta_text')
        form.cta_link.data = settings.get('cta_link')
        form.background_color.data = settings.get('background_color', '#007bff') # provide default if missing
        form.text_color.data = settings.get('text_color', '#FFFFFF') # provide default if missing
        form.position.data = settings.get('position', 'top') # provide default

    return render_template('hellobar/create_edit_hellobar.html', title='Edit Hello Bar', form=form, legend=f'Edit {campaign.name}', campaign_id=campaign.id)

@hellobar_bp.route('/<int:campaign_id>/delete', methods=['POST'])
@login_required
def delete_hellobar(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner != current_user or campaign.campaign_type != 'hello_bar':
        flash('You do not have permission to delete this campaign or it is not a Hello Bar.', 'danger')
        return redirect(url_for('hellobar.list_hellobars'))
    db.session.delete(campaign)
    db.session.commit()
    flash('Hello Bar campaign deleted successfully!', 'success')
    return redirect(url_for('hellobar.list_hellobars'))

@hellobar_bp.route('/<int:campaign_id>/snippet')
@login_required
def get_snippet(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner != current_user or campaign.campaign_type != 'hello_bar':
        return jsonify(error="Permission denied or not a Hello Bar campaign"), 403
    if not campaign.is_active:
        # Allowing to get snippet for inactive bar for testing, but it won't auto-display if logic is added
        # flash('This Hello Bar is not active. The snippet will not display anything until activated.', 'warning')
        pass # Or return error: return jsonify(error="This Hello Bar is not active."), 400


    settings = json.loads(campaign.settings) if campaign.settings else {}

    message_text = settings.get('message_text', '').replace('\\', '\\\\').replace('"', '\"').replace('\n', '\\n')
    cta_text = settings.get('cta_text', '').replace('\\', '\\\\').replace('"', '\"').replace('\n', '\\n')
    cta_link = settings.get('cta_link', '').replace('\\', '\\\\').replace('"', '\"').replace('\n', '\\n')
    position = settings.get('position', 'top')
    background_color = settings.get('background_color', '#007bff')
    text_color = settings.get('text_color', '#FFFFFF')

    snippet = (
        '<!-- Campaign SaaS Tool - Hello Bar Snippet -->\n'
        '<script type="text/javascript">\n'
        '(function() {\n'
        f'    var bar = document.createElement("div");\n'
        f'    bar.id = "cst-hello-bar-{campaign_id}";\n'
        f'    var message = document.createElement("span");\n'
        f'    message.innerText = "{message_text}";\n'
        f'    bar.appendChild(message);\n'
        '\n'
        f'    var ctaText = "{cta_text}";\n'
        f'    var ctaLink = "{cta_link}";\n'
        f'    if (ctaText && ctaLink) {{\n'
        f'        var cta = document.createElement("a");\n'
        f'        cta.innerText = ctaText;\n'
        f'        cta.href = ctaLink;\n'
        f'        cta.target = "_blank";\n'
        f'        cta.style.marginLeft = "15px";\n'
        f'        cta.style.padding = "5px 10px";\n'
        f'        cta.style.backgroundColor = "#fff"; /* Example style */\n'
        f'        cta.style.color = "#000"; /* Example style */\n'
        f'        cta.style.textDecoration = "none";\n'
        f'        cta.style.borderRadius = "3px";\n'
        f'        bar.appendChild(cta);\n'
        f'    }}\n'
        '\n'
        f'    var closeBtn = document.createElement("span");\n'
        f'    closeBtn.innerHTML = "&times;";\n'
        f'    closeBtn.style.marginLeft = "15px";\n'
        f'    closeBtn.style.cursor = "pointer";\n'
        f'    closeBtn.style.fontWeight = "bold";\n'
        f'    closeBtn.onclick = function() {{ bar.style.display = "none"; }};\n'
        f'    bar.appendChild(closeBtn);\n'
        '\n'
        f'    bar.style.position = "fixed";\n'
        f'    bar.style.{position} = "0";\n'
        f'    bar.style.left = "0";\n'
        f'    bar.style.width = "100%";\n'
        f'    bar.style.padding = "10px";\n'
        f'    bar.style.backgroundColor = "{background_color}";\n'
        f'    bar.style.color = "{text_color}";\n'
        f'    bar.style.textAlign = "center";\n'
        f'    bar.style.zIndex = "9999";\n'
        f'    bar.style.boxSizing = "border-box";\n'
        '\n'
        f'    /* Only append if the bar does not already exist */ \n'
        f'    if (!document.getElementById(bar.id)) {{ \n'
        f'        document.body.appendChild(bar);\n'
        f'        if ("{position}" === "top") {{\n'
        f'            var barHeight = bar.offsetHeight;\n'
        f'            var currentPaddingTop = parseInt(window.getComputedStyle(document.body).paddingTop, 10) || 0;\n'
        f'            document.body.style.paddingTop = (currentPaddingTop + barHeight) + "px";\n'
        f'        }}\n'
        f'    }}\n'
        f'}})();\n'
        '</script>\n'
        '<!-- End Hello Bar Snippet -->'
    )
    # The snippet above has literal \n for display in textarea, JS itself uses actual newlines.
    # For the template, ensure it's passed as a single block of text.
    return render_template('hellobar/snippet.html', title="Hello Bar Snippet", snippet_code=snippet.replace('\n', '\r\n'), campaign_name=campaign.name)

EOF
