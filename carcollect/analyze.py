import os, sys, subprocess, shlex, re, datetime, base64

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app, send_from_directory
)

from subprocess import call
from numpy import arange, take
from pydub import AudioSegment
from ffprobe import FFProbe
from matplotlib.figure import Figure
from io import BytesIO
from scipy.io import wavfile as wav
from scipy.fftpack import fft, fftfreq

from carcollect.filemanager import upload, uploads, uploaded_file
from carcollect.account import login_required

import matplotlib.pyplot as plt
import numpy as np

bp = Blueprint('analyze', __name__, url_prefix='/analyze')

ALLOWED_EXTENSIONS = ['mp3', 'wav']
PATH = 'analyze'

@bp.route('/upload', methods=('GET', 'POST'))
def audiofile_upload():
    """Redirects user to upload page
    
    Returns:
        template -- upload page
    """
    return upload(PATH, ALLOWED_EXTENSIONS)


@bp.route('/uploads', methods=('GET', 'POST'))
@login_required
def audiofile_uploads():
    """Redirects user to uploads while passing some params
    
    Returns:
        template -- uploads page
    """
    return uploads(PATH)


def read_audiofile(path):
    """read .wav files and return data.

    Args:
        path (str): Path to file including filename

    Returns:
        array, array: fs_rate and signal
    """
    fs_rate, signal = wav.read(path)
    metadata = probe_file(path)
    
    print('audiofile read...')

    return fs_rate, signal, metadata


def probe_file(filename):
    """Method to get metadata from audiofile
    
    Arguments:
        filename {str} -- path to file
    
    Returns:
        list -- metadata key=value pairs
    """
    cmnd = ['ffprobe', '-show_entries', 
        'stream=codec_long_name,sample_rate,channels,bits_per_sample,duration,bit_rate:format=format_long_name,size', 
        '-pretty', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()        
    metadata = out.decode("utf-8").split("\n")
    error = err.decode("utf-8")
    print(error)
    
    return metadata


def convert_mp3_to_wav(source):
    """convert mp3 files to wav format.

    Args:
        source (str): path to mp3 file

    Returns:
        str: path to converted file
    """
    filename = os.path.basename(source)

    new_filename = f'{filename.split(".")[0]}.wav'
    saving_destination = os.path.abspath(os.path.join(current_app.config['UPLOAD_FOLDER'], PATH, new_filename))

    AudioSegment.from_mp3(source).export(saving_destination, format="wav")

    os.remove(source)
    new_path = os.path.join(current_app.config['UPLOAD_FOLDER'], PATH, new_filename)

    return new_path


def get_plot_data(fs_rate, signal, filename):
    """Plot graphs with audio data.

    Args:
        fs_rate (array): fs_rate
        signal (array): signal values
        filename (str): filename

    Returns:
        data: encoded base64 graph data
    """
    audiofile = AudioFile(fs_rate, signal, filename)
    audiofile.analyze_all()

    figures = collect_figures(audiofile)
    data = encode_to_base64(figures)
    return data


def encode_to_base64(figures):
    """Summary.

    Args:
        audiofile (AudioFile): AudioFile object

    Returns:
        data: encoded base64 graph data
    """
    data = []  
    for figure in figures: 
        buf = BytesIO()
        figure.savefig(buf, format="png")

        figure_data = base64.b64encode(buf.getbuffer()).decode("ascii")
        data.append(figure_data)

    return data


def collect_figures(audiofile):
    """Generate plot showing waveform
    
    Arguments:
        audiofile {AudioFile} -- AudioFile object
    
    Returns:
        Figure -- generated figure using audio data
    """
    fig_signal = plot_fig(audiofile.t, audiofile.data)
    fig_fft_spectrum = plot_fig(audiofile.freqs, audiofile.FFT)
    fig_pos_fft_sectrum = plot_fig(audiofile.freqs_side, audiofile.FFT_side)

    figures = [fig_signal, fig_fft_spectrum, fig_pos_fft_sectrum]

    return figures


def plot_fig(x, y):
    """Plots a figure
    
    Arguments:
        x {collection} -- x-axis data
        y {collection} -- y-axis data
    
    Returns:
        Figure -- matplotlib.Figure
    """
    fig = Figure()
    ax = fig.subplots()
    ax.plot(x, y)

    return fig


def save_plot(plt, filename):
    """Save a pyplot object as png
    
    Arguments:
        plt {pyplot.plot} -- the plot that needs saving
        filename {str} -- filename without extension
    """
    plt.savefig('{}/{}.png'.format(current_app.config['PLOT_FOLDER'], filename.split('.')[0]))


@bp.route('/plot', methods=('GET', 'POST'))
def plot_waveform():
    """Main method that initiates the analyzation of an audiofile. Also calls
    all nesseccery functions.

    Returns:
        Redirect object: redirect to 'uploaded_file' page
    """
    if request.method == "POST":
        filename = request.form["filename"]
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], PATH, filename)
        data = None
        metadata = None
        try:
            if needs_conversion(filename):
                path = convert_mp3_to_wav(path)
                filename = os.path.basename(path)       
            try:       
                fs_rate, signal, metadata = read_audiofile(path)
            except ValueError:
                flash('Cannot read file, make sure the file uses a .wav or .mp3 format')
            data = get_plot_data(fs_rate, signal, filename)
        except FileNotFoundError:
            flash('Something went wrong while trying to find the correct file. Please contact blablabla.....', 'error')
        
    return uploaded_file(filename, data, metadata)


def needs_conversion(filename):
    """Simple check whether a file needs conversion to .wav
    
    Arguments:
        filename {str} -- filename including extension      
    
    Returns:
        bool -- [description]
    """
    return filename.split('.')[1] == "mp3"


class AudioFile():
    """Simple class representing an audiofile. Houses all the needed variables
    """
    def __init__(self, sample_rate, data, filename):
        self.sample_rate = sample_rate
        print('sample rate:', self.sample_rate)
        self.data = data
        print("signal length:", len(self.data))
        print('signal example:', self.data)
        self.filename = filename
        print('filename:', filename)

    
    def analyze_all(self):
        """Analyzes the audiofile data and saves it in local variables
        """
        self._analyze_channels()
        self._analyze_samplings()
        self._analyze_length()
        self._analyze_sample_interval()
        self._vector_to_arange()
        self._apply_fft()       
        print('analysis complete..')


    def _analyze_channels(self):
        """analyzes the amount of audio channels existing in the file
        """
        self.channels = len(self.data.shape)
        print("data shape:", self.data.shape)
        print("file has", self.channels, "audio channels")
        if self.channels == 2:
            self.data = self.data.sum(axis=1) / 2
            print('example 2 channel data:', self.data)


    def _analyze_samplings(self):
        """analyzes the total amount of samples
        """
        self.samples_ammount = self.data.shape[0]
        print("total samplings N:", self.samples_ammount)


    def _analyze_length(self):
        """analyzes the total length of the file
        """
        self.secs = self.samples_ammount / float(self.sample_rate)
        print("sound length:", str(datetime.timedelta(seconds=int(self.secs))))


    def _analyze_sample_interval(self):
        """analyzes the time between samples
        """
        self.sample_time = 1.0 / self.sample_rate 
        print("sample time:", self.sample_time)

    
    def _vector_to_arange(self):
        """creates the time vector with a scipy arange field
        """
        self.t = arange(0, self.secs, self.sample_time) 
        print(f'time vector: start = 0, end = {self.secs}, steps = {self.sample_time}')

    
    def _apply_fft(self):
        """does all the necessery fft calculations
        """
        print('data to be transformed:', self.data, 'length:', len(self.data))
        self.FFT = abs(fft(self.data))
        print('fft completed, data:', self.FFT, "length:", len(self.FFT))
        self.FFT_side = self.FFT[range(self.samples_ammount // 2)]  
        print('FFT_side = total amount of samples / 2')
        self.freqs = fftfreq(self.data.size, self.t[1] - self.t[0])
        print('calculated frequencies')
        self.fft_freqs = np.array(self.freqs)
        print('frequencies to np.array')
        self.freqs_side = self.freqs[range(self.samples_ammount // 2)] 
        print('calculated one side of frequency range')


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