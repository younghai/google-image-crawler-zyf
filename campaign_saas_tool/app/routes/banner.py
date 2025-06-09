from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.campaign import Campaign
from app.forms import BannerForm # Ensure this is imported
import json

banner_bp = Blueprint('banner', __name__)

@banner_bp.route('/list')
@login_required
def list_banners():
    banners = Campaign.query.filter_by(owner=current_user, campaign_type='banner').order_by(Campaign.created_at.desc()).all()
    return render_template('banner/list_banners.html', title='My Banners', banners=banners)

@banner_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_banner():
    form = BannerForm()
    if form.validate_on_submit():
        settings = {
            'image_url': form.image_url.data,
            'link_url': form.link_url.data,
            'position_type': form.position_type.data,
            'target_div_id': form.target_div_id.data if form.position_type.data == 'inline_replace' else None,
            'width': form.width.data,
            'height': form.height.data,
        }
        banner_campaign = Campaign(
            name=form.name.data,
            campaign_type='banner',
            is_active=form.is_active.data,
            owner=current_user,
            settings=json.dumps(settings)
        )
        db.session.add(banner_campaign)
        db.session.commit()
        flash('Banner campaign created successfully!', 'success')
        return redirect(url_for('banner.list_banners'))
    return render_template('banner/create_edit_banner.html', title='Create Banner', form=form, legend='New Banner Campaign')

@banner_bp.route('/<int:campaign_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_banner(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner != current_user or campaign.campaign_type != 'banner':
        flash('You do not have permission to edit this campaign or it is not a Banner.', 'danger')
        return redirect(url_for('banner.list_banners'))

    form = BannerForm()
    if form.validate_on_submit():
        settings = {
            'image_url': form.image_url.data,
            'link_url': form.link_url.data,
            'position_type': form.position_type.data,
            'target_div_id': form.target_div_id.data if form.position_type.data == 'inline_replace' else None,
            'width': form.width.data,
            'height': form.height.data,
        }
        campaign.name = form.name.data
        campaign.is_active = form.is_active.data
        campaign.settings = json.dumps(settings)
        db.session.commit()
        flash('Banner campaign updated successfully!', 'success')
        return redirect(url_for('banner.list_banners'))
    elif request.method == 'GET':
        settings = json.loads(campaign.settings) if campaign.settings else {}
        form.name.data = campaign.name
        form.is_active.data = campaign.is_active
        form.image_url.data = settings.get('image_url')
        form.link_url.data = settings.get('link_url')
        form.position_type.data = settings.get('position_type', 'inline_replace')
        form.target_div_id.data = settings.get('target_div_id')
        form.width.data = settings.get('width', '300px')
        form.height.data = settings.get('height', '250px')

    return render_template('banner/create_edit_banner.html', title='Edit Banner', form=form, legend=f'Edit {campaign.name}', campaign_id=campaign.id)

@banner_bp.route('/<int:campaign_id>/delete', methods=['POST'])
@login_required
def delete_banner(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner != current_user or campaign.campaign_type != 'banner':
        flash('You do not have permission to delete this campaign or it is not a Banner.', 'danger')
        return redirect(url_for('banner.list_banners'))
    db.session.delete(campaign)
    db.session.commit()
    flash('Banner campaign deleted successfully!', 'success')
    return redirect(url_for('banner.list_banners'))

@banner_bp.route('/<int:campaign_id>/snippet')
@login_required
def get_snippet(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner != current_user or campaign.campaign_type != 'banner':
        return jsonify(error="Permission denied or not a Banner campaign"), 403
    # Allow getting snippet for inactive campaigns for setup purposes
    # if not campaign.is_active:
    #     return jsonify(error="This Banner is not active."), 400

    settings = json.loads(campaign.settings) if campaign.settings else {}

    image_url = settings.get('image_url', '').replace('"', '\"')
    link_url = settings.get('link_url', '').replace('"', '\"')
    position_type = settings.get('position_type', 'inline_replace')
    target_div_id = settings.get('target_div_id', f'cst-banner-placeholder-{campaign_id}').replace('"', '\"')
    width = settings.get('width', '300px').replace('"', '\"')
    height = settings.get('height', '250px').replace('"', '\"')

    snippet_js_lines = [
        '(function() {',
        f'    var campaignId = {campaign_id};',
        f'    var imageUrl = "{image_url}";',
        f'    var linkUrl = "{link_url}";',
        f'    var positionType = "{position_type}";',
        f'    var targetDivId = "{target_div_id}";',
        f'    var bannerWidth = "{width}";',
        f'    var bannerHeight = "{height}";',
        '',
        '    if (!imageUrl) { console.error("CST Banner: Image URL is missing."); return; }',
        '',
        '    var anchor = document.createElement("a");',
        '    anchor.href = linkUrl;',
        '    anchor.target = "_blank"; // Optional: open in new tab',
        '',
        '    var img = document.createElement("img");',
        '    img.src = imageUrl;',
        '    img.style.width = bannerWidth;',
        '    img.style.height = bannerHeight;',
        '    img.style.border = "0"; // Optional: remove border from linked images',
        '    anchor.appendChild(img);',
        '',
        '    var container;',
        '    if (positionType === "inline_replace") {',
        '        container = document.getElementById(targetDivId);',
        '        if (container) {',
        '            container.innerHTML = ""; // Clear the placeholder',
        '            container.appendChild(anchor);',
        '        } else {',
        '            console.error("CST Banner: Target DIV with ID \'" + targetDivId + "\' not found for inline banner.");',
        '            return;',
        '        }',
        '    } else {',
        '        container = document.createElement("div");',
        '        container.id = "cst-banner-fixed-" + campaignId;',
        '        container.style.position = "fixed";',
        '        container.style.zIndex = "9998"; // Below hello bar potentially',
        '        container.style.width = bannerWidth;',
        '        container.style.height = bannerHeight;',
        '        if (positionType === "fixed_bottom_right") { container.style.bottom = "10px"; container.style.right = "10px"; }',
        '        else if (positionType === "fixed_bottom_left") { container.style.bottom = "10px"; container.style.left = "10px"; }',
        '        else if (positionType === "fixed_top_right") { container.style.top = "10px"; container.style.right = "10px"; }',
        '        else if (positionType === "fixed_top_left") { container.style.top = "10px"; container.style.left = "10px"; }',
        '        container.appendChild(anchor);',
        '        if (!document.getElementById(container.id)) { document.body.appendChild(container); }',
        '    }',
        '})();'
    ]
    snippet = (
        f'<!-- Campaign SaaS Tool - Banner Snippet (Campaign ID: {campaign_id}) -->\n'
        '<script type="text/javascript">\n' +
        '\n'.join(snippet_js_lines) +
        '\n</script>\n'
        f'<!-- End Banner Snippet. For "Inline" type, ensure a div with ID "{target_div_id}" exists. -->'
    )

    # For inline_replace, provide the placeholder div too
    placeholder_html = ""
    if position_type == "inline_replace":
        placeholder_html = f'<div id="{target_div_id}"></div> <!-- CST Banner Placeholder -->'

    return render_template('banner/snippet.html',
                           title="Banner Snippet",
                           snippet_code=snippet.replace('\n', '\r\n'),
                           placeholder_html=placeholder_html,
                           campaign_name=campaign.name,
                           position_type=position_type,
                           target_div_id=target_div_id)
