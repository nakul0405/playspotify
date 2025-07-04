@app.route("/autologin")
def autologin():
    return render_template("login.html")
