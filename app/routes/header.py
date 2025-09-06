from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home/home.html", title="ホーム")


@app.route("/post")
def post():
    return render_template("photograph/post.html", title="投稿")


@app.route("/post_past")
def post_past():
    return render_template("photograph/post_past.html", title="過去の投稿")


@app.route("/personal_page")
def personal_page():
    return render_template("personal_page/personal_page.html", title="マイページ")


@app.route("/personal_settings")
def personal_settings():
    return render_template(
        "personal_page/personal_settings.html", title="プロフィール設定"
    )


if __name__ == "__main__":
    app.run(debug=True)
