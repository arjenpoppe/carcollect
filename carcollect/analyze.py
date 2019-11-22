import os
import base64

from pydub import AudioSegment

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app, send_from_directory
)

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from io import BytesIO
from scipy import arange
from scipy.io import wavfile as wav
from scipy.fftpack import fft, fftfreq
import numpy as np

from carcollect.filemanager import upload, uploads, uploaded_file
from carcollect.account import login_required

bp = Blueprint('analyze', __name__, url_prefix='/analyze')

ALLOWED_EXTENSIONS = ['mp3', 'wav']
PATH = 'analyze'

# reroute to the upload page
@bp.route('/upload', methods=('GET', 'POST'))
def audiofile_upload():
    return upload(PATH, ALLOWED_EXTENSIONS)


# reroute to the file list
@bp.route('/uploads', methods=('GET', 'POST'))
@login_required
def audiofile_uploads():
    return uploads(PATH)


# read and convert file to .wav
def read_audiofile(path):
    fs_rate, signal = wav.read(path)

    return fs_rate, signal

def convert_mp3_to_wav(source):
    test = source
    filename = os.path.basename(source)
    print('source: ' + test)

    new_filename = f'{filename.split(".")[0]}.wav'
    saving_destination = os.path.abspath(os.path.join(current_app.config['UPLOAD_FOLDER'], PATH, new_filename))


    # convert wav to mp3
    AudioSegment.from_mp3(source).export(saving_destination, format="wav")
    
    flash("File has been converted to the .wav format")

    # delete old file
    os.remove(source)

    new_path = os.path.join(current_app.config['UPLOAD_FOLDER'], PATH, new_filename)


    return new_path


def plot_graphs(fs_rate, signal, filename):
    
    # TODO fix this

    # print("Frequency sampling", fs_rate)
    l_audio = len(signal.shape)
    # print("Channels", l_audio)
    if l_audio == 2:
        signal = signal.sum(axis=1) / 2
    N = signal.shape[0]
    # print("Complete Samplings N", N)
    secs = N / float(fs_rate)
    # print("secs", secs)
    Ts = 1.0 / fs_rate  # sampling interval in time
    # print("Timestep between samples Ts", Ts)
    t = arange(0, secs, Ts)  # time vector as scipy arange field / numpy.ndarray

    FFT = abs(fft(signal))
    FFT_side = FFT[range(N // 2)]  # one side FFT range
    freqs = fftfreq(signal.size, t[1] - t[0])
    fft_freqs = np.array(freqs)
    freqs_side = freqs[range(N // 2)]  # one side frequency range

    t_divider = int(len(t)/1000)
    freq_divider = int(len(freqs_side)/1000)

    # # plotting the signal
    # plt.subplot(311)
    # p1 = plt.plot(t[::t_divider], signal[::t_divider], "g")
    # plt.xlabel('Time [in 100 miliseconds]')
    # plt.ylabel('Amplitude')

    # # plotting the complete fft spectrum
    # plt.subplot(312)
    # p2 = plt.plot(freqs[::t_divider], FFT[::t_divider], "r")
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Count dbl-sided')

    # # plotting the positive fft spectrum
    # plt.subplot(313)
    # p3 = plt.plot(freqs_side[::freq_divider], abs(FFT_side)[::freq_divider], "b")
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Count single-sided')

    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    return data

    # save_plot(plt, filename)


# save plot in predefined location
def save_plot(plt, filename):
    plt.savefig('{}/{}.png'.format(current_app.config['PLOT_FOLDER'], filename.split('.')[0]))


# Main method that initiates the sound analysis
@bp.route('/plot', methods=('GET', 'POST'))
def plot_waveform():
    if request.method == "POST":
        filename = request.form["filename"]
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], PATH, filename)
        data = None
        try:
            # convert file if necessery
            if needs_conversion(filename):
                print('file_path: ' + path)
                path = convert_mp3_to_wav(path)
                filename = os.path.basename(path)
            
            # read audio file
            try:       
                fs_rate, signal = read_audiofile(path)
            except ValueError:
                flash('Cannot read file, make sure the file uses a .wav or .mp3 format')

            #plot and save graphs
            data = plot_graphs(fs_rate, signal, filename)
        except FileNotFoundError:
            flash('Something went wrong while trying to find the correct file. Please contact blablabla.....', 'error')
        

    return uploaded_file(filename, data)


def needs_conversion(filename):
    return filename.split('.')[1] == "mp3"

