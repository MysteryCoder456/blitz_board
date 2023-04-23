from quart import Quart, render_template

app = Quart(__name__)


@app.route("/")
async def landing_page():
    return await render_template("landing.html")


def run():
    app.run(debug=True)
