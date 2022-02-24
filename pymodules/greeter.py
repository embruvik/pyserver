def greeter(name, greeting="Hello",**kwargs):
    if kwargs:
        style = kwargs['style']
    else:
        style = '!'
    
    return 'Py: ' + greeting + name + style