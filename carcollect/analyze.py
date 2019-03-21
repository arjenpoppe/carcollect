import functools
import os

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app, send_from_directory
)
from werkzeug.utils import secure_filename

import matplotlib.pyplot as plt
from scipy import arange
from scipy.io import wavfile as wav
from scipy.fftpack import fft, fftfreq
import numpy as np

from carcollect.db import get_db

bp = Blueprint('analyze', __name__, url_prefix='/analyze')

ALLOWED_EXTENSIONS = set(['mp3', 'wav'])
# current_app.config['PLOT_FOLDER'] = '/plots'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/upload', methods=('GET', 'POST'))
def upload():
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


@bp.route('/uploads')
def uploads():
    filelist = os.listdir(current_app.config['UPLOAD_FOLDER'])

    return render_template('analyze/uploads.html', filelist=filelist)


@bp.route('/uploads/<filename>', methods=('GET', 'POST'))
def uploaded_file(filename):
    plot_waveform(filename)
    name = filename.split('.')[0]
    extension = filename.split('.')[1]

    return render_template('analyze/uploaded_file.html', filename=name, extension=extension)


def plot_waveform(filename):
    # rate, data = wav.read('{}/{}'.format(current_app.config['UPLOAD_FOLDER'], filename))
    #
    # # convert potential stereo sound to mono by averaging the left and right channel
    # data = np.mean(data, axis=1)
    #
    # # calculate the length of the audio file
    # N = data.shape[0]
    # L = N / rate
    #
    # # print audio length in console
    # print(f'Audio length: {L:.2f} seconds')
    #
    # f, ax = plt.subplots()
    # ax.plot(np.arange(N) / rate, data)
    # ax.set_xlabel('Time [s]')
    # ax.set_ylabel('Amplitude [unknown]');
    # plt.savefig('{}/{}.png'.format(current_app.config['PLOT_FOLDER'], filename.split('.')[0]))

    fs_rate, signal = wav.read('{}/{}'.format(current_app.config['UPLOAD_FOLDER'], filename))
    print("Frequency sampling", fs_rate)
    l_audio = len(signal.shape)
    print("Channels", l_audio)
    if l_audio == 2:
        signal = signal.sum(axis=1) / 2
    N = signal.shape[0]
    print("Complete Samplings N", N)
    secs = N / float(fs_rate)
    print("secs", secs)
    Ts = 1.0 / fs_rate  # sampling interval in time
    print("Timestep between samples Ts", Ts)
    t = arange(0, secs, Ts)  # time vector as scipy arange field / numpy.ndarray
    FFT = abs(fft(signal))
    FFT_side = FFT[range(N // 2)]  # one side FFT range
    freqs = fftfreq(signal.size, t[1] - t[0])
    fft_freqs = np.array(freqs)
    freqs_side = freqs[range(N // 2)]  # one side frequency range
    fft_freqs_side = np.array(freqs_side)
    plt.subplot(311)
    p1 = plt.plot(t, signal, "g")  # plotting the signal
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.subplot(312)
    p2 = plt.plot(freqs, FFT, "r")  # plotting the complete fft spectrum
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Count dbl-sided')
    plt.subplot(313)
    p3 = plt.plot(freqs_side, abs(FFT_side), "b")  # plotting the positive fft spectrum
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Count single-sided')
    plt.savefig('{}/{}.png'.format(current_app.config['PLOT_FOLDER'], filename.split('.')[0]))


# @bp.route('/fft_test', methods=('GET', 'POST'))
# def fft_test():
#
#     return render_template('analyze/fft_test.html')
