import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from flask import Flask, json, redirect, render_template, request, url_for

app = Flask(__name__)


class PostInterface(ABC):
    @abstractmethod
    def to_dict(self):
        """Convert the post to a dictionary."""
        pass


class BlogPost(PostInterface):
    def __init__(self, author, title, content, id=None):
        self.id = id or uuid.uuid4().hex
        self.author = author
        self.title = title
        self.content = content

    def to_dict(self):
        """Convert the blog post to a dictionary."""
        return {
            "id": self.id,
            "author": self.author,
            "title": self.title,
            "content": self.content,
        }


class BlogManagerInterface(ABC):
    @abstractmethod
    def load_posts(self):
        """Load blog posts from storage."""
        pass

    @abstractmethod
    def save_posts(self, posts):
        """Save blog posts to storage."""
        pass

    @abstractmethod
    def add_post(self, author, title, content):
        """Add a new blog post."""
        pass

    @abstractmethod
    def delete_post(self, post_id):
        """Delete a blog post by ID."""
        pass

    @abstractmethod
    def update_post(self, post_id, author, title, content):
        """Update a blog post by ID."""
        pass


class BlogManager(BlogManagerInterface):
    def __init__(self, file_path):
        self.file_path = Path(file_path)

    def load_posts(self):
        """Load blog posts from the JSON file."""
        try:
            with self.file_path.open("r") as file:
                post_dicts = json.load(file)
                return [BlogPost(**post_dict) for post_dict in post_dicts]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_posts(self, posts):
        """Save blog posts to the JSON file."""
        with self.file_path.open("w") as file:
            json.dump([post.to_dict() for post in posts], file, indent=4)

    def add_post(self, author, title, content):
        """Add a new blog post."""
        post = BlogPost(author=author, title=title, content=content)
        posts = self.load_posts()
        posts.append(post)
        self.save_posts(posts)

    def delete_post(self, post_id):
        """Delete a blog post by ID."""
        posts = self.load_posts()
        posts = [post for post in posts if post.id != post_id]
        self.save_posts(posts)

    def update_post(self, post_id, author, title, content):
        """Update a blog post by ID."""
        posts = self.load_posts()
        for post in posts:
            if post.id == post_id:
                post.author = author
                post.title = title
                post.content = content
                self.save_posts(posts)
                return True
        return False


# Initialize BlogManager with the path to the JSON file
blog_manager = BlogManager("storage/blog_data.json")


@app.route("/")
def index():
    blog_posts = blog_manager.load_posts()
    return render_template("index.html", posts=[post.to_dict() for post in blog_posts])


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        if not validate_form_data(request.form):
            return render_template("error.html", message="All fields are required.")
        blog_manager.add_post(
            author=request.form["author"],
            title=request.form["title"],
            content=request.form["content"],
        )
        return redirect(url_for("index"))
    return render_template("add.html")


@app.route("/delete/<string:post_id>", methods=["POST"])
def delete(post_id):
    blog_manager.delete_post(post_id)
    return redirect(url_for("index"))


def validate_form_data(form):
    return all(form.get(field) for field in ["author", "title", "content"])


@app.route("/update/<string:post_id>", methods=["GET", "POST"])
def update(post_id):
    if request.method == "POST":
        if not validate_form_data(request.form):
            return render_template("error.html", message="All fields are required.")
        success = blog_manager.update_post(
            post_id,
            author=request.form["author"],
            title=request.form["title"],
            content=request.form["content"],
        )
        if not success:
            return render_template("error.html", message="Post not found.")
        return redirect(url_for("index"))

    posts = blog_manager.load_posts()
    for post in posts:
        if post.id == post_id:
            return render_template("update.html", post=post.to_dict())

    return render_template("error.html", message="Post not found.")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
