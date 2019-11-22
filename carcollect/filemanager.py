import os

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app, send_from_directory
)
from werkzeug.utils import secure_filename

from carcollect.account import login_required

bp = Blueprint('filemanager', __name__, url_prefix='/files')


# returns whether file type is allowed or not
def allowed_file(filename, allowed_extensions):
    if not allowed_extensions:
        return '.' in filename
    else:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_file(path, file):
    """Summary
    
    Args:
        path (TYPE): Description
        file (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    filename = secure_filename(file.filename)
    save_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], path)

    if not os.path.isdir(save_dir):
        os.mkdir(save_dir,)
    file.save(os.path.join(save_dir, filename))
    return filename


# Generic upload page. Can be used for specific extensions and paths
@bp.route('/upload', methods=('GET', 'POST'))
def upload(path='', allowed_extensions=[]):
    print(path, allowed_extensions)
    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file found')
            return redirect(request.url)
        file = request.files['file']

        # check if file type is allowed
        if not allowed_file(file.filename, allowed_extensions):
            flash('File type not allowed')
            return redirect(request.url)

        # if file exists and of the right file type, file will be uploaded
        if file and allowed_file(file.filename, allowed_extensions):
            
            filename = save_file(path, file)
            flash('file {} uploaded successfully'.format(filename))

            # return redirect(url_for('filemanager.uploaded_file', filename=filename))
    if allowed_extensions:
        flashmsg = "Allowed extensions: " + ", ".join(allowed_extensions)
        flash(flashmsg, 'error')
    return render_template('files/upload_file.html', allowed_extensions=allowed_extensions)


@bp.route('/')
@bp.route('/<dir>')
@login_required
def uploads(dir=''):
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], dir)

    # breakpoint()

    if os.path.isdir(path):
        filelist = os.listdir(path)
        return render_template('files/uploads.html', filelist=filelist)
    else:
        return uploaded_file(dir)


@bp.route('/<filename>')
def uploaded_file(filename, data=None):
    name = filename.split('.')[0]
    extension = filename.split('.')[1]

    return render_template('files/uploaded_file.html', filename=name, extension=extension, data=data)