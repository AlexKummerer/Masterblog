import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    json,
    redirect,
    render_template,
    request,
    url_for,
)
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


class PostInterface(ABC):
    @abstractmethod
    def to_dict(self):
        """Convert the post to a dictionary."""
        pass


class BlogPost(PostInterface):
    def __init__(self, author, title, content, id=None, likes=0):
        self.id = id or uuid.uuid4().hex
        self.author = author
        self.title = title
        self.content = content
        self.likes = likes

    def to_dict(self):
        """Convert the blog post to a dictionary."""
        return {
            "id": self.id,
            "author": self.author,
            "title": self.title,
            "content": self.content,
            "likes": self.likes,
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
        original_count = len(posts)
        posts = [post for post in posts if post.id != post_id]

        if len(posts) == original_count:
            return False  # Post not found

        self.save_posts(posts)
        return True

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

    def like_post(self, post_id):
        """Like a blog post by ID."""
        posts = self.load_posts()
        for post in posts:
            if post.id == post_id:
                post.likes += 1
                self.save_posts(posts)
                return True
        return False


# Initialize BlogManager with the path to the JSON file
blog_manager = BlogManager("storage/blog_data.json")


@app.route("/")
def index():
    blog_posts = blog_manager.load_posts()
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "index.html", posts=[post.to_dict() for post in blog_posts], messages=messages
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        if not validate_form_data(request.form):
            flash("All fields are required.", "error")
            return render_template("add.html")
        blog_manager.add_post(
            author=request.form["author"],
            title=request.form["title"],
            content=request.form["content"],
        )
        flash("Post added successfully!", "success")
        return redirect(url_for("index"))
    return render_template("add.html")


@app.route("/delete/<string:post_id>", methods=["POST"])
def delete(post_id):
    success = blog_manager.delete_post(post_id)
    if not success:
        flash("Post not found.", "error")
        return redirect(url_for("index"))
    flash("Post deleted successfully!", "success")
    return redirect(url_for("index"))


def validate_form_data(form):
    return all(form.get(field) for field in ["author", "title", "content"])


@app.route("/update/<string:post_id>", methods=["GET", "POST"])
def update(post_id):
    if request.method == "POST":
        if not validate_form_data(request.form):
            flash("All fields are required.", "error")
            return redirect(url_for("update", post_id=post_id))

        success = blog_manager.update_post(
            post_id,
            author=request.form["author"],
            title=request.form["title"],
            content=request.form["content"],
        )

        if not success:
            flash("Post not found.", "error")
            return redirect(url_for("index"))

        flash("Post updated successfully!", "success")
        return redirect(url_for("index"))

    posts = blog_manager.load_posts()
    for post in posts:
        if post.id == post_id:
            return render_template("update.html", post=post.to_dict())

    flash("Post not found.", "error")
    return redirect(url_for("index"))


@app.route("/like/<string:post_id>", methods=["POST"])
def like(post_id):
    success = blog_manager.like_post(post_id)
    if not success:
        flash("Post not found.", "error")
        return redirect(url_for("index"))

    flash("Post liked!", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
