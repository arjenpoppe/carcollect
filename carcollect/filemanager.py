import os

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app, send_from_directory
)

from werkzeug.utils import secure_filename
from carcollect.account import login_required

bp = Blueprint('filemanager', __name__, url_prefix='/files')


def allowed_file(filename, allowed_extensions):
    """Simple check whether file type is allowed or not
    
    Args:
        filename (str): complete filename
        allowed_extensions (list, set): allowed file extensions
    
    Returns:
        BOOLEAN: extensions allowed yes/no
    """
    if not allowed_extensions:
        return '.' in filename
    else:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_file(path, file):
    """Save an uploaded file on the host server
    
    Args:
        path (str): path where the file should be saved, relative from default upload path
        file (file): The file object itself
    
    Returns:
        str: Filename
    """
    filename = secure_filename(file.filename)
    save_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], path)

    if not os.path.isdir(save_dir):
        os.mkdir(save_dir,)
    file.save(os.path.join(save_dir, filename))
    print('file saved to filesystem...')
    return filename


@bp.route('/upload', methods=('GET', 'POST'))
def upload(path='', allowed_extensions=[]):
    '''Generic upload page.
    
    Args:
        path (str, optional): path to which the file should be saved
        allowed_extensions (list, optional): allowed file extensions
    
    Returns:
        render_template: Upload template
    '''
    if request.method == 'POST':

        file = request.files['file']

        if file.filename == '':
            flash('No file found', 'error')
            return redirect(request.url)
        
        # check if file type is allowed
        if not allowed_file(file.filename, allowed_extensions):
            flash('File type not allowed', 'error')
            return redirect(request.url)

        # if file exists and of the right file type, file will be uploaded
        if file and allowed_file(file.filename, allowed_extensions):
            filename = save_file(path, file)
            flash('file {} uploaded successfully'.format(filename), 'success')

            # return redirect(url_for('filemanager.uploaded_file', filename=filename))
    if allowed_extensions:
        flashmsg = "Allowed extensions: " + ", ".join(allowed_extensions)
        flash(flashmsg)
    return render_template('files/upload_file.html', allowed_extensions=allowed_extensions)


@bp.route('/')
@bp.route('/<dir>')
@login_required
def uploads(dir=''):
    """returns 'uploads' view
    
    Args:
        dir (str, optional): starting directory
    
    Returns:
        redirect/template: view with filelist or uploaded_file page
    """
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], dir)

    if os.path.isdir(path):
        filelist = os.listdir(path)
        return render_template('files/uploads.html', filelist=filelist)
    else:
        return uploaded_file(dir)


@bp.route('/<filename>')
def uploaded_file(filename, data=None, metadata=None):
    """Simple view of the selected file
    
    Args:
        filename (str): Description
        data (base64 graph data, optional): Description
    
    Returns:
        template: 'files/uploaded_file.html'
    """
    return render_template('files/uploaded_file.html', filename=filename, data=data, metadata=metadata)