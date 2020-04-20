from app import db, app

DEBUG = True
db.create_all()

if DEBUG:
    app.run('localhost', 1000, DEBUG)

else:
    app.run('0.0.0.0', 80, DEBUG)