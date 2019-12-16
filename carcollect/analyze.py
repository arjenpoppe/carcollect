import os
import base64

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app, send_from_directory
)

import matplotlib.pyplot as plt
import numpy as np

from pydub import AudioSegment
from matplotlib.figure import Figure
from io import BytesIO
from scipy import arange
from scipy.io import wavfile as wav
from scipy.fftpack import fft, fftfreq

from carcollect.filemanager import upload, uploads, uploaded_file
from carcollect.account import login_required

bp = Blueprint('analyze', __name__, url_prefix='/analyze')

ALLOWED_EXTENSIONS = ['mp3', 'wav']
PATH = 'analyze'

@bp.route('/upload', methods=('GET', 'POST'))
def audiofile_upload():
    # reroute to the upload page
    return upload(PATH, ALLOWED_EXTENSIONS)


@bp.route('/uploads', methods=('GET', 'POST'))
@login_required
def audiofile_uploads():
    # reroute to the file list
    return uploads(PATH)


def read_audiofile(path):
    """read .wav files and return data
    
    Args:
        path (str): Path to file including filename
    
    Returns:
        array, array: fs_rate and signal
    """
    fs_rate, signal = wav.read(path)

    return fs_rate, signal


def convert_mp3_to_wav(source):
    """convert mp3 files to wav format
    
    Args:
        source (str): path to mp3 file
    
    Returns:
        str: path to converted file
    """
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
    """Plot graphs with audio data
    
    Args:
        fs_rate (array): fs_rate
        signal (array): signal values
        filename (str): filename
    
    Returns:
        data: encoded base64 graph data
    """
    audiofile = AudioFile(fs_rate, signal, filename)
    audiofile.analyze()
    return create_multiplot(audiofile)


def create_multiplot(audiofile):
    """Summary
    
    Args:
        audiofile (AudioFile): AudioFile object
    
    Returns:
        data: encoded base64 graph data
    """
    t_divider = int(len(audiofile.t)/1000)
    # freq_divider = int(len(audiofile.freqs_side)/1000)

    # TODO figure out what method to use

    # # plotting the signal
    # plt.subplot(311)
    # p1 = plt.plot(audiofile.t[::t_divider], audiofile.signal[::t_divider], "g")
    # plt.xlabel('Time [in 100 miliseconds]')
    # plt.ylabel('Amplitude')

    # # plotting the complete fft spectrum
    # plt.subplot(312)
    # p2 = plt.plot(audiofile.freqs[::t_divider], audiofile.FFT[::t_divider], "r")
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Count dbl-sided')

    # # plotting the positive fft spectrum
    # plt.subplot(313)
    # p3 = plt.plot(audiofile.freqs_side[::freq_divider], abs(audiofile.FFT_side)[::freq_divider], "b")
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Count single-sided')

    # save_plot(plt, audiofile.filename)

    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot(audiofile.t[::t_divider], audiofile.signal[::t_divider])
    
    # Save to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    return data


def save_plot(plt, filename):
    # save plot in predefined location
    plt.savefig('{}/{}.png'.format(current_app.config['PLOT_FOLDER'], filename.split('.')[0]))


@bp.route('/plot', methods=('GET', 'POST'))
def plot_waveform():
    """Main method that initiates the analyzation of an audiofile. Also calls all nesseccery 
    functions
    
    Returns:
        Redirect object: redirect to 'uploaded_file' page
    """
    if request.method == "POST":
        filename = request.form["filename"]
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], PATH, filename)
        data = None
        try:
            if needs_conversion(filename):
                print('file_path: ' + path)
                path = convert_mp3_to_wav(path)
                filename = os.path.basename(path)
            
            try:       
                fs_rate, signal = read_audiofile(path)
            except ValueError:
                flash('Cannot read file, make sure the file uses a .wav or .mp3 format')

            data = plot_graphs(fs_rate, signal, filename)

        except FileNotFoundError:
            flash('Something went wrong while trying to find the correct file. Please contact blablabla.....', 'error')
        
    return uploaded_file(filename, data)


def needs_conversion(filename):
    return filename.split('.')[1] == "mp3"


class AudioFile():

    """Summary
    
    Attributes:
        channels (TYPE): Description
        FFT (TYPE): Description
        fft_freqs (TYPE): Description
        FFT_side (TYPE): Description
        filename (TYPE): Description
        freqs (TYPE): Description
        freqs_side (TYPE): Description
        fs_rate (TYPE): Description
        N (TYPE): Description
        secs (TYPE): Description
        signal (TYPE): Description
        t (TYPE): Description
        Ts (TYPE): Description
    """
    
    def __init__(self, fs_rate, signal, filename):
        self.fs_rate = fs_rate
        self.signal = signal
        self.filename = filename

    def analyze(self):
        self.channels = len(self.signal.shape)
        # print("Channels", channels)
        if self.channels == 2:
            self.signal = self.signal.sum(axis=1) / 2
        self.N = self.signal.shape[0]
        # print("Complete Samplings N", N)
        self.secs = self.N / float(self.fs_rate)
        # print("secs", secs)
        self.Ts = 1.0 / self.fs_rate  # sampling interval in time
        # print("Timestep between samples Ts", Ts)
        self.t = arange(0, self.secs, self.Ts)  # time vector as scipy arange field / numpy.ndarray

        self.FFT = abs(fft(self.signal))
        self.FFT_side = self.FFT[range(self.N // 2)]  # one side FFT range
        self.freqs = fftfreq(self.signal.size, self.t[1] - self.t[0])
        self.fft_freqs = np.array(self.freqs)
        self.freqs_side = self.freqs[range(self.N // 2)]  # one side frequency range


