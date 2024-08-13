from flask import Flask, render_template

app = Flask(__name__)

blog_posts = [
    {
        "id": 1,
        "author": "John Doe",
        "title": "First Post",
        "content": "This is my first post.",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Second Post",
        "content": "This is another post.",
    },
    {
        "id": 3,
        "author": "John Doe",
        "title": "Third Post",
        "content": "This is yet another post.",
    },
    {
        "id": 4,
        "author": "Jane Doe",
        "title": "Fourth Post",
        "content": "This is the last post.",
    },
    {
        "id": 5,
        "author": "John Doe",
        "title": "Fifth Post",
        "content": "This is the fifth post.",
    }
]


@app.route("/")
def index():
    # add code here to fetch the job posts from a file
    return render_template("index.html", posts=blog_posts)


if __name__ == "__main__":
    app.run(debug=True)
