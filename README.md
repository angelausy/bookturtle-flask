# BookTurtle

## Installation (Mac OS X)
To run the application with your computer as a server, you'll need Python installed. First, open the Terminal and clone this repository:

    git clone https://github.com/angelausy/bookturtle-flask.git

Next, create a virtual environment for the application and its dependencies:

    virtualenv env
    source env/bin/activate
    pip install flask
    pip install -r requirements.txt
    
Create a settings_local.py file with the following contents:

    import os
    GOODREADS_API_KEY = XXX
    SHELFIE_ACCESS_KEY = XXX
    SHELFIE_SECRET_KEY = XXX
    DEPLOY_ENV = 'local'

You should then be able to launch the app with your computer as the server. When you type:

    python app.py

You should see:

    * Running on http://127.0.0.1:5000/
    * Restarting with reloader

To start using the app, type this URL into your browser:

    http://localhost:5000
