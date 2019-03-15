import functools
import os

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app
)
from werkzeug.utils import secure_filename


from carcollect.db import get_db

bp = Blueprint('analyze', __name__, url_prefix='/analyze')

ALLOWED_EXTENSIONS = set(['mp3'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/upload_file', methods=('GET', 'POST'))
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if not allowed_file(file.filename):
            flash('File type not allowed')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            flash('file {} uploaded successfully'.format(filename))
            return redirect(url_for('analyze.upload_file'))
    return render_template('analyze/upload_file.html')
