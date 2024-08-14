import random
import uuid
from flask import Flask, json, redirect, render_template, request, url_for

app = Flask(__name__)


@app.route("/")
def index():
    with open("storage/blog_data.json") as user_file:
        blog_posts = json.load(user_file)
    return render_template("index.html", posts=blog_posts)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        post = {
            "id": uuid.uuid4().hex,
            "author": request.form["author"],
            "title": request.form["title"],
            "content": request.form["content"],
        }

        with open("storage/blog_data.json", "r") as user_file:
            blog_posts = json.load(user_file)

        blog_posts.append(post)

        with open("storage/blog_data.json", "w") as user_file:
            json.dump(blog_posts, user_file, indent=4)

        return redirect(url_for("index"))

        # add code here to save the job post to a file
    return render_template("add.html")


@app.route("/delete/<string:post_id>", methods=["POST"])
def delete(post_id):
    with open("storage/blog_data.json", "r") as user_file:
        blog_posts = json.load(user_file)

    for post in blog_posts:
        if post["id"] == post_id:
            blog_posts.remove(post)

    with open("storage/blog_data.json", "w") as user_file:
        json.dump(blog_posts, user_file, indent=4)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
