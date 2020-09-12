from utils import URLShortener
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)
urls = URLShortener()

@app.route('/', methods=['GET', 'POST'])
def create_new():
    if request.method == 'GET':
        return render_template("index.html")
    elif request.method == 'POST':
        url = request.form["url"]
        password = request.form["password"]
        key, password = (url[-6:], password) if password else urls.create_new(url)
        return redirect("/analytics/{}?password={}".format(key, password), code=302)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route("/analytics/<key>", methods=['GET', 'POST'])
def get_analytics(key):
    obj = urls.get_object(key, inc_count=False)
    password = request.args.get("password", None)
    if key and password and obj and password == obj["password"]:
        if request.method == 'GET':
            return render_template("page_analytics.html",
                                   domain=request.host_url,
                                   url=obj["url"],
                                   key=obj["key"],
                                   password=obj["password"],
                                   count=obj["count"])
        elif request.method == 'POST':
            urls.remove_obj(key, password)
            return redirect("/",  code=302)
    else:
        return "Wrong short URL or password"


@app.route('/<key>')
def redirect_to_url(key):
    obj = urls.get_object(key)
    if obj:
        return redirect(obj["url"] if obj["url"] else "/", code=302)
    return "Wrong short URL"


if __name__ == '__main__':
    app.run()
