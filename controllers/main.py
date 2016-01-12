import hill

def main():
    return 'hello main'

def index():
    t = hill.Template('index.html')
    return t.render(name='index', id='110')
