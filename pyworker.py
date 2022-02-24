import importlib
import inspect
import sys
import socket
import json
from pathlib import Path
from copy import copy
import os

gFunctions = {}
class FunctionWrapper:
    def __init__(self,funcname,function):
        self.funcname = funcname
        self.function = function
        self.signature = inspect.signature(function)
        self.args = {}

        for a in self.signature.parameters:
            default = self.signature.parameters[a].default
            if default == inspect._empty:
                self.args[a] = None
            else:
                self.args[a] = default
        

    def __call__(self, argumentsobj):
        
        argsobj = copy(argumentsobj)
        posargs = []
        for arg,default in self.args.items():
            if arg == 'kwargs':
                break
            argval = argsobj.get(arg)
            if argval:
                posargs.append(argval)
            else:
                if default:
                    posargs.append(default)
                else:
                    raise ValueError("FW: calling ", self.funcname, " could not find value for parameter: ", arg)
            if argval:
                argsobj.pop(arg)

        return self.function(*posargs,**argsobj)

# open socket to server
sockname = sys.argv[1]
print("Worker will connect to: ",sockname)
s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
s.connect(sockname)
s.send(b"OK")

# load modules
print("Pyworker looking for modules:")
sys.path.append('./pymodules')
files = Path('pymodules').glob('*')
for f in files:
    #print(f.name)
    importname = ''
    if f.is_dir():
        try:
            os.stat(f / '__init__.py')
            importname = f.name
        except FileNotFoundError:
            pass
    else:
        if f.name.endswith('.py') and not f.name.startswith('__'):
            importname = f.name[:-3]

    if importname:
        print('  Found import: ', importname)
        # sys.path.append('./pymodules')
        module = importlib.import_module(importname)
        mf = inspect.getmembers(module,inspect.isfunction)
        for fn,f in mf:
            print("   Found function: ",fn)
            gFunctions[fn] = FunctionWrapper(fn,f)

while True:
    nbr = int.from_bytes(s.recv(4),'little',signed=True)
    call = json.loads(s.recv(nbr))
    print("Pyworker got request: ", str(call))

    error={}
    clientwants = call.get('function')
    if not clientwants:
        error['message'] = 'No \"function\" specified!'
    else:
        if not clientwants in gFunctions:
            error['message'] = f'Function {clientwants} is not loaded as a callable function.'
        else:
            if not 'args' in call:
                error['message'] = 'No args specified!'
            else:
                # do call
                try:
                    retval = gFunctions[clientwants](call['args'])
                except Exception as e:
                    error['message'] = f'An exception occurred during call to {clientwants}'
                    error['exception'] = repr(e)
    if not error:
        toreturn = bytes(json.dumps(retval).encode('utf-8'))
    else:
        print("ERROR!!! - in pyworker:")
        toreturn = bytes(json.dumps(error).encode('utf-8'))
    nbr = int.to_bytes(len(toreturn),4,'little', signed=True)
    s.send(nbr)
    s.sendall(toreturn)

