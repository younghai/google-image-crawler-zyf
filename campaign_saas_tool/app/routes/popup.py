from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.campaign import Campaign
from app.forms import PopupForm # Ensure this is imported
import json

popup_bp = Blueprint('popup', __name__)

@popup_bp.route('/list')
@login_required
def list_popups():
    popups = Campaign.query.filter_by(owner=current_user, campaign_type='popup').order_by(Campaign.created_at.desc()).all()
    return render_template('popup/list_popups.html', title='My Popups', popups=popups)

@popup_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_popup():
    form = PopupForm()
    if form.validate_on_submit():
        settings = {
            'popup_type': form.popup_type.data,
            'title': form.title.data,
            'custom_html_content': form.custom_html_content.data if form.popup_type.data == 'custom_html' else None,
            'youtube_video_id': form.youtube_video_id.data if form.popup_type.data == 'youtube_video' else None,
            'trigger_type': form.trigger_type.data,
            'trigger_delay': form.trigger_delay.data,
            'display_frequency': form.display_frequency.data,
            'width': form.width.data,
            # 'height': form.height.data,
            'overlay_color': form.overlay_color.data,
        }
        popup_campaign = Campaign(
            name=form.name.data,
            campaign_type='popup',
            is_active=form.is_active.data,
            owner=current_user,
            settings=json.dumps(settings)
        )
        db.session.add(popup_campaign)
        db.session.commit()
        flash('Popup campaign created successfully!', 'success')
        return redirect(url_for('popup.list_popups'))
    return render_template('popup/create_edit_popup.html', title='Create Popup', form=form, legend='New Popup Campaign')

@popup_bp.route('/<int:campaign_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_popup(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner != current_user or campaign.campaign_type != 'popup':
        flash('Permission denied or not a Popup campaign.', 'danger')
        return redirect(url_for('popup.list_popups'))

    form = PopupForm()
    if form.validate_on_submit():
        settings = {
            'popup_type': form.popup_type.data,
            'title': form.title.data,
            'custom_html_content': form.custom_html_content.data if form.popup_type.data == 'custom_html' else None,
            'youtube_video_id': form.youtube_video_id.data if form.popup_type.data == 'youtube_video' else None,
            'trigger_type': form.trigger_type.data,
            'trigger_delay': form.trigger_delay.data,
            'display_frequency': form.display_frequency.data,
            'width': form.width.data,
            # 'height': form.height.data,
            'overlay_color': form.overlay_color.data,
        }
        campaign.name = form.name.data
        campaign.is_active = form.is_active.data
        campaign.settings = json.dumps(settings)
        db.session.commit()
        flash('Popup campaign updated successfully!', 'success')
        return redirect(url_for('popup.list_popups'))
    elif request.method == 'GET':
        settings = json.loads(campaign.settings) if campaign.settings else {}
        form.name.data = campaign.name
        form.is_active.data = campaign.is_active
        form.popup_type.data = settings.get('popup_type', 'custom_html')
        form.title.data = settings.get('title')
        form.custom_html_content.data = settings.get('custom_html_content')
        form.youtube_video_id.data = settings.get('youtube_video_id')
        form.trigger_type.data = settings.get('trigger_type', 'on_load')
        form.trigger_delay.data = settings.get('trigger_delay', 3)
        form.display_frequency.data = settings.get('display_frequency', 'once_per_session')
        form.width.data = settings.get('width', '600px')
        # form.height.data = settings.get('height', 'auto')
        form.overlay_color.data = settings.get('overlay_color', 'rgba(0,0,0,0.5)')

    return render_template('popup/create_edit_popup.html', title='Edit Popup', form=form, legend=f'Edit {campaign.name}', campaign_id=campaign.id)

@popup_bp.route('/<int:campaign_id>/delete', methods=['POST'])
@login_required
def delete_popup(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner != current_user or campaign.campaign_type != 'popup':
        flash('Permission denied or not a Popup campaign.', 'danger')
        return redirect(url_for('popup.list_popups'))
    db.session.delete(campaign)
    db.session.commit()
    flash('Popup campaign deleted successfully!', 'success')
    return redirect(url_for('popup.list_popups'))

@popup_bp.route('/<int:campaign_id>/snippet')
@login_required
def get_snippet(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner != current_user or campaign.campaign_type != 'popup':
        return jsonify(error="Permission denied or not a Popup campaign"), 403

    settings = json.loads(campaign.settings) if campaign.settings else {}

    # Escape data for JS
    popup_type = settings.get('popup_type', 'custom_html')
    title = settings.get('title', '').replace('"', '\"').replace('\n', '\\n')
    custom_html_content = settings.get('custom_html_content', '').replace('\`', '\\`').replace('${', '\${').replace('"', '\"').replace('\n', '\\n') # Careful with backticks and template literals
    youtube_video_id = settings.get('youtube_video_id', '').replace('"', '\"')
    trigger_type = settings.get('trigger_type', 'on_load')
    trigger_delay = settings.get('trigger_delay', 3) * 1000 # Convert to ms
    display_frequency = settings.get('display_frequency', 'once_per_session')
    popup_width = settings.get('width', '600px').replace('"', '\"')
    overlay_color = settings.get('overlay_color', 'rgba(0,0,0,0.5)').replace('"', '\"')
    is_active = campaign.is_active # Get from campaign model directly

    snippet_js_lines = [
        f'var CST_POPUP_CONFIG_{campaign_id} = {{',
        f'  campaignId: {campaign_id},',
        f'  isActive: {"true" if is_active else "false"},',
        f'  popupType: "{popup_type}",',
        f'  title: "{title}",',
        # For custom_html, ensure it's properly escaped for a JS string literal
        f'  customHtmlContent: `{" ".join(custom_html_content.splitlines())}`,', # Use template literal for multi-line HTML
        f'  youtubeVideoId: "{youtube_video_id}",',
        f'  triggerType: "{trigger_type}",',
        f'  triggerDelay: {trigger_delay},',
        f'  displayFrequency: "{display_frequency}",',
        f'  popupWidth: "{popup_width}",',
        f'  overlayColor: "{overlay_color}",',
        f'  sessionStorageKey: "cstPopupShown_{campaign_id}"',
        '};',
        '',
        '(function(config) {',
        '  if (!config.isActive) return;',
        '',
        '  function hasBeenShownThisSession() {',
        '    if (config.displayFrequency === "once_per_session") {',
        '      try { return sessionStorage.getItem(config.sessionStorageKey) === "true"; } catch (e) { return false; }',
        '    }',
        '    return false; // For "every_time" or unhandled cases',
        '  }',
        '',
        '  function markAsShownThisSession() {',
        '    if (config.displayFrequency === "once_per_session") {',
        '      try { sessionStorage.setItem(config.sessionStorageKey, "true"); } catch (e) { /* ignore */ }',
        '    }',
        '  }',
        '',
        '  if (hasBeenShownThisSession()) return;',
        '',
        '  function showPopup() {',
        '    if (document.getElementById("cst-popup-overlay-" + config.campaignId)) return; // Already shown',
        '',
        '    var overlay = document.createElement("div");',
        '    overlay.id = "cst-popup-overlay-" + config.campaignId;',
        '    overlay.style.position = "fixed"; overlay.style.top = "0"; overlay.style.left = "0";',
        '    overlay.style.width = "100%"; overlay.style.height = "100%";',
        '    overlay.style.backgroundColor = config.overlayColor; overlay.style.zIndex = "99998";',
        '    overlay.style.display = "flex"; overlay.style.alignItems = "center"; overlay.style.justifyContent = "center";',
        '',
        '    var contentWrapper = document.createElement("div");',
        '    contentWrapper.style.backgroundColor = "#fff"; contentWrapper.style.padding = "20px";',
        '    contentWrapper.style.borderRadius = "5px"; contentWrapper.style.width = config.popupWidth;',
        '    contentWrapper.style.maxWidth = "90%"; contentWrapper.style.maxHeight = "90vh";',
        '    contentWrapper.style.overflowY = "auto"; contentWrapper.style.position = "relative";',
        '    contentWrapper.style.boxShadow = "0 4px 15px rgba(0,0,0,0.2)";',
        '',
        '    var closeButton = document.createElement("span");',
        '    closeButton.innerHTML = "&times;";',
        '    closeButton.style.position = "absolute"; closeButton.style.top = "10px"; closeButton.style.right = "15px";',
        '    closeButton.style.fontSize = "24px"; closeButton.style.cursor = "pointer"; closeButton.style.fontWeight = "bold";',
        '    closeButton.onclick = function() { overlay.remove(); };',
        '    contentWrapper.appendChild(closeButton);',
        '',
        '    if (config.title) {',
        '      var titleElem = document.createElement("h3"); titleElem.innerText = config.title;',
        '      titleElem.style.marginTop = "0"; titleElem.style.marginBottom = "15px";',
        '      contentWrapper.appendChild(titleElem);',
        '    }',
        '',
        '    if (config.popupType === "youtube_video" && config.youtubeVideoId) {',
        '      var videoContainer = document.createElement("div");',
        '      videoContainer.style.position = "relative"; videoContainer.style.paddingBottom = "56.25%"; /* 16:9 */',
        '      videoContainer.style.height = "0"; videoContainer.style.overflow = "hidden";',
        '      var iframe = document.createElement("iframe");',
        '      iframe.src = "https://www.youtube.com/embed/" + config.youtubeVideoId + "?autoplay=1";',
        '      iframe.style.position = "absolute"; iframe.style.top = "0"; iframe.style.left = "0";',
        '      iframe.style.width = "100%"; iframe.style.height = "100%";',
        '      iframe.setAttribute("frameborder", "0");',
        '      iframe.setAttribute("allow", "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture");',
        '      iframe.setAttribute("allowfullscreen", "");',
        '      videoContainer.appendChild(iframe);',
        '      contentWrapper.appendChild(videoContainer);',
        '    } else if (config.popupType === "custom_html") {',
        '      var htmlContentDiv = document.createElement("div");',
        '      htmlContentDiv.innerHTML = config.customHtmlContent;',
        '      contentWrapper.appendChild(htmlContentDiv);',
        '    }',
        '',
        '    overlay.appendChild(contentWrapper);',
        '    document.body.appendChild(overlay);',
        '    markAsShownThisSession();',
        '  }',
        '',
        '  if (config.triggerType === "on_load") {',
        '    if (document.readyState === "complete") {',
        '      setTimeout(showPopup, config.triggerDelay);',
        '    } else {',
        '      window.addEventListener("load", function() { setTimeout(showPopup, config.triggerDelay); });',
        '    }',
        '  }',
        '})(CST_POPUP_CONFIG_{campaign_id});'
    ]
    snippet = (
        f'<!-- Campaign SaaS Tool - Popup Snippet (Campaign ID: {campaign_id}) -->\n'
        '<script type="text/javascript">\n' +
        '\n'.join(snippet_js_lines) +
        '\n</script>\n'
        '<!-- End Popup Snippet -->'
    )

    return render_template('popup/snippet.html',
                           title="Popup Snippet",
                           snippet_code=snippet.replace('\n', '\r\n'),
                           campaign_name=campaign.name,
                           campaign=campaign) # Pass campaign for snippet preview button
EOF
