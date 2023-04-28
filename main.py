from site import addsitedir
import sys


### this isn't needed when you run the file through venv/scripts/python.exe
sitedir = r"G:\1-School work\Formulate3D\Flask tests\venv\Lib\site-packages"
try:
    addsitedir(sitedir)
except:
    sys.exit(0)
    
from website import create_app, checks, create_admin

checks()

app = create_app()

if __name__== '__main__':
    app.run(debug=True)
