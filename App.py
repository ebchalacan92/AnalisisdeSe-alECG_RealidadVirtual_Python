import numpy as np
from scipy.signal import butter, lfilter
import scipy.signal
from pywt import wavedec
from scipy.interpolate import interp1d
import scipy.io
from flask import Flask, render_template
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import find_peaks
import pyrebase



app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    hola = analisis()
    return render_template('about.html',contactos=hola)

@app.route('/imagenes')
def imagenes():
    return render_template('imagenes.html')

@app.route('/informacion')
def informacion():
    return render_template('informacion.html')

   
rate = 360
archivo= scipy.io.loadmat('D:/Datos Importantes/UCE/UCE/9.- Noveno/Optativa 3/Proyecto/chalacan-Optativa01/src/118m.mat')
arreglo_val= archivo['val']
m=np.array(arreglo_val[0])

def bandpass_filter( values ):
    nyquist_freq= rate
    low = 0.1 / nyquist_freq
    high = 25.0 / nyquist_freq
    b, a = butter( 5, [low, high], btype ="band")
    y = lfilter( b, a, values )
       
    return y

def Dwavelet_filter(y):
    levels=4
    C= wavedec(y, 'db7', level= levels)
    filtered_1a= C[levels - 1]
    filtered_2a= C[levels]
        
    xnew = np.arange(len(y))
        
    time_1= np.linspace(0, len(y), len(filtered_1a), endpoint=True)
    filtered_1= interp1d(time_1, filtered_1a)(xnew)
        
    time_2= np.linspace(0, len(y), len(filtered_2a), endpoint=True)
    filtered_2= interp1d(time_2, filtered_2a)(xnew)
    filtered= filtered_1 + filtered_2
    fil_ind = list(filtered)
       
    return fil_ind

def Detect_ecg_peaks(x):
    y0= np.ediff1d(x)
    y1= y0 ** 2
    y2= np.convolve(y1, np.ones(22))
    return y2

def Arrhytmia_detection(x):
    indexes= scipy.signal.find_peaks_cwt(x, np.arange(10, 24))
    indexe= np.array(indexes) - 1
    heart_rate= len(indexe) * 2
    return heart_rate


def analisis():
    values_ecg= m
    butter_filter= bandpass_filter(values_ecg)
    wave_filter= Dwavelet_filter(butter_filter)
    deri_ecg= Detect_ecg_peaks(wave_filter)
    TB= Arrhytmia_detection(deri_ecg)

    fig1=plt.figure(1)
    coeffs = wavedec(m, 'db7', level=4)
    sig_detrend=signal.detrend(m)
    fig1, ax = plt.subplots (len (coeffs) +1)
    ax[0].plot(sig_detrend)
    for i, coeffs in enumerate(coeffs):
        ax[i+1].plot(coeffs)

    fig2 = plt.figure(2)
    peaks,_ = find_peaks(m, height=0)
    fig1 = plt.figure(1)
    plt.plot(m)
    plt.plot(peaks, m[peaks], "o")
    fig1.savefig("ecg.png", dpi=fig1.dpi)
    fig2.savefig("dist.png", dpi=fig2.dpi)

    #Credenciales para la comunicación
    config = {
        "apiKey": "AIzaSyCDcxH6lr9y2s-U-sltFLRR9P2vttagAVE",
        "authDomain": "test-dff08.firebaseapp.com",
        "databaseURL": "https://test-dff08.firebaseio.com",
        "projectId": "test-dff08",
        "storageBucket": "test-dff08.appspot.com",
        "messagingSenderId": "517614321740",
        "appId": "1:517614321740:web:7d361c99b4fd7af34634e9",
        "measurementId": "G-DH2SZWXCF3"
    }
    #Inicializa la base de datos
    firebase = pyrebase.initialize_app(config)
    #Subir una imagen a Storage
    storage = firebase.storage()
    storage.child("images/ecg.png").put("ecg.png")
    storage.child("images/dist.png").put("dist.png")
    mensaje = "Imagenes Guardadas en Firebase"
    
    if TB < 60:
        latidos = str(TB)
        numero = "BRADICARDIA, Número de latidos : "
        enfermedad = numero + latidos + " >>>> "+ mensaje      
    elif TB > 100:
        latidos = str(TB)
        numero = "TAQUICARDIA, Número de latidos : "
        enfermedad = numero + latidos + " >>>> "+ mensaje            
    else:
        latidos = str(TB)
        numero = "FRECUENCIA NORMAL, Número de latidos : "
        enfermedad = numero + latidos + " >>>> "+ mensaje      
         
    return enfermedad


if __name__ == '__main__':
    app.run(port=5000, debug=True)
    
    


