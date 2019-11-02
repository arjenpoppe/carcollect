import os

from pydub import AudioSegment

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app, send_from_directory
)

import matplotlib.pyplot as plt
from scipy import arange
from scipy.io import wavfile as wav
from scipy.fftpack import fft, fftfreq
import numpy as np

from carcollect.filemanager import upload, uploads

bp = Blueprint('analyze', __name__, url_prefix='/analyze')

ALLOWED_EXTENSIONS = set(['mp3', 'wav'])
PATH = 'analyze'


# index page for the sound analysis process
@bp.route('/')
def show_overview():
    return render_template('analyze/overview.html')


# reroute to the upload page
@bp.route('/upload', methods=('GET', 'POST'))
def audiofile_upload():
    return upload(PATH, ALLOWED_EXTENSIONS)


# reroute to the file list
@bp.route('/uploads', methods=('GET', 'POST'))
def audiofile_uploads():
    return uploads(PATH)


# read and convert file to .wav
def read_audiofile(filename):
    source = os.path.join(current_app.config['UPLOAD_FOLDER'], PATH, filename)
    filename_no_extension, extension = filename.split('.')[0], filename.split('.')[1]
    destination = os.path.abspath(os.path.join(current_app.config['UPLOAD_FOLDER'], PATH,
                                               f'{filename_no_extension}.wav'))
    if 'mp3' in extension:
        # convert wav to mp3
        flash('source is: ' + source)
        flash('destination is: ' + destination)

        # convert wav to mp3
        AudioSegment.from_mp3(source).export(destination, format="wav")
        flash("File has been converted to the .wav format")

        # delete old file
        os.remove(source)

    fs_rate, signal = wav.read(destination)

    return fs_rate, signal


# plot waveform graphs using fft and audio data
def plot_graphs(filename):
    fs_rate, signal = read_audiofile(filename)
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

    # breakpoint()

    t_divider = int(len(t)/1000)
    freq_divider = int(len(freqs_side)/1000)

    # breakpoint()

    # plotting the signal
    plt.subplot(311)
    p1 = plt.plot(t[::t_divider], signal[::t_divider], "g")
    plt.xlabel('Time [in 100 miliseconds]')
    plt.ylabel('Amplitude')

    # plotting the complete fft spectrum
    plt.subplot(312)
    p2 = plt.plot(freqs[::t_divider], FFT[::t_divider], "r")
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Count dbl-sided')

    # plotting the positive fft spectrum
    plt.subplot(313)
    p3 = plt.plot(freqs_side[::freq_divider], abs(FFT_side)[::freq_divider], "b")
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Count single-sided')
    save_plot(plt, filename)


# save plot in predefined location
def save_plot(plt, filename):
    plt.savefig('{}/{}.png'.format(current_app.config['PLOT_FOLDER'], filename.split('.')[0]))


# Main method that initiates the sound analysis
@bp.route('/plot/<filename>', methods=('GET', 'POST'))
def plot_waveform(filename):
    try:
        plot_graphs(filename)
    except ValueError:
        flash('Cannot read file, make sure the file uses a .wav or .mp3 format')

    return redirect(url_for('filemanager.uploaded_file', filename=filename))
