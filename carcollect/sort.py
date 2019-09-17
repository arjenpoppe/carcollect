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

bp = Blueprint('sort', __name__, url_prefix='/sort')