import functools
import os

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app, send_from_directory
)
from werkzeug.utils import secure_filename

import matplotlib.pyplot as plt
from scipy.io import wavfile as wav
from scipy.fftpack import fft
import numpy as np

from carcollect.db import get_db

bp = Blueprint('analyze', __name__, url_prefix='/analyze')

ALLOWED_EXTENSIONS = set(['mp3', 'wav'])


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
            return redirect(url_for('analyze.uploaded_file', filename=filename))
    return render_template('analyze/upload_file.html')


@bp.route('/uploads/<filename>', methods=('GET', 'POST'))
def uploaded_file(filename):
    return render_template('analyze/uploads.html', filename=filename)


@bp.route('/fft_test', methods=('GET', 'POST'))
def fft_test():
    rate, data = wav.read('{}/test.wav'.format(current_app.config['UPLOAD_FOLDER']))
    fft_out = fft(data)

    plt.plot(data, np.abs(fft_out))
    plt.show()
