import matplotlib.pyplot as plt
import numpy as np
import io
import base64

def plotter(title):
    fh = plt.figure()
    plt.title('Py: ' + title)
    x = np.linspace(0,10,100)
    s = np.sin(x)
    plt.plot(x,s,'r-',label='sine')
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf,format='png')

    buf.seek(0)
    return {'fig': (b"data:image/png;charset=utf-8;base64,"+base64.encodebytes(buf.read())).decode('utf-8')}
