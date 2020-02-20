from server import app

debug = True

if debug:
    app.run(debug=debug)
else:
    app.run('0.0.0.0')