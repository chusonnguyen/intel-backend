from Capstone import create_app
import os

#run web server
app= create_app()
if __name__ == '__main__':
    app.run()