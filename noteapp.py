import flask
import models
import forms
import acl

from flask_login import login_required, login_user, logout_user

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
models.init_app(app)


@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()
    return flask.render_template(
        "index.html",
        notes=notes,
    )


@app.route("/home")
def home():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()
    return flask.render_template(
        "home.html",
        notes=notes,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm()
    if not form.validate_on_submit():
        return flask.render_template(
            "login.html",
            form=form,
        )
    user = models.User.query.filter_by(username=form.username.data).first()

    if user and user.authenticate(form.password.data):
        login_user(user)
        return flask.redirect(flask.url_for("home"))

    return flask.redirect(flask.url_for("login", error="Invalid username or password"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = forms.RegisterForm()
    if not form.validate_on_submit():
        return flask.render_template(
            "register.html",
            form=form,
        )

    user = models.User()  # Initialize the user here
    form.populate_obj(user)  # Populate the user object with form data

    role = models.Role.query.filter_by(name="user").first()
    if not role:  # Create the 'user' role if it doesn't exist
        role = models.Role(name="user")
        models.db.session.add(role)

    user.roles.append(role)
    user.password_hash = form.password.data
    models.db.session.add(user)
    models.db.session.commit()

    return flask.redirect(flask.url_for("home"))


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()
    return flask.render_template(
        "tags_view.html",
        tag_name=tag_name,
        notes=notes,
    )


@app.route("/tags/<tag_id>/update_tags", methods=["GET", "POST"])
def update_tags(tag_id):  # แก้ไข Tags ได้
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.id == tag_id))
        .scalars()
        .first()
    )
    form = forms.TagsForm()
    form_name = tag.name

    if not form.validate_on_submit():
        print(form.errors)
        return flask.render_template("update_tags.html", form=form, form_name=form_name)

    note = models.Note(id=tag_id)
    form.populate_obj(note)
    tag.name = form.name.data
    db.session.commit()

    return flask.redirect(flask.url_for("home"))


@app.route("/tags/<tag_id>/delete_tags", methods=["GET", "POST"])
def delete_tags(tag_id):  # ลบ Tags ได้อย่างเดียว
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.id == tag_id))
        .scalars()
        .first()
    )

    tag.name = ""
    db.session.commit()

    return flask.redirect(flask.url_for("home"))


@app.route("/notes/create_note", methods=["GET", "POST"])
def create_note():
    form = forms.NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "create_note.html",
            form=form,
        )
    note = models.Note()
    form.populate_obj(note)
    note.tags = []

    db = models.db
    for tag_name in form.tags.data:
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )

        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)

        note.tags.append(tag)

    db.session.add(note)
    db.session.commit()

    return flask.redirect(flask.url_for("home"))


@app.route("/tags/<tag_id>/update_note", methods=["GET", "POST"])
def update_note(tag_id):  # แก้ไข Note และสามารถเปลี่ยนชื่อ Title ได้
    db = models.db
    notes = (
        db.session.execute(
            db.select(models.Note).where(models.Note.tags.any(id=tag_id))
        )
        .scalars()
        .first()
    )
    form = forms.NoteForm()
    form_title = notes.title
    form_description = notes.description
    if not form.validate_on_submit():
        print(form.errors)
        return flask.render_template(
            "update_note.html",
            form=form,
            form_title=form_title,
            form_description=form_description,
        )

    note = models.Note(id=tag_id)
    form.populate_obj(note)
    notes.description = form.description.data
    notes.title = form.title.data
    db.session.commit()

    return flask.redirect(flask.url_for("home"))


@app.route("/tags/<tag_id>/delete_note", methods=["GET", "POST"])
def delete_note(tag_id):  # ลบ Note เพียงอย่างเดียวไม่ได้ลบ Title
    db = models.db
    notes = (
        db.session.execute(
            db.select(models.Note).where(models.Note.tags.any(id=tag_id))
        )
        .scalars()
        .first()
    )
    notes.description = ""
    db.session.commit()

    return flask.redirect(flask.url_for("home"))


@app.route("/tags/<tag_id>/delete", methods=["GET", "POST"])
def delete(tag_id):  # ลบทั้งหมดที่เกี่ยวกับ Tags
    db = models.db
    notes = (
        db.session.execute(
            db.select(models.Note).where(models.Note.tags.any(id=tag_id))
        )
        .scalars()
        .first()
    )
    db.session.delete(notes)
    db.session.commit()
    return flask.redirect(flask.url_for("home"))


@app.route("/profile")
def profile():
    db = models.db
    user = db.session.execute(
        db.select(models.User).order_by(models.User.name)
    ).scalars()
    return flask.render_template(
        "profile.html",
        user=user,
    )


@app.route("/people")
def people():
    db = models.db
    users = db.session.execute(
        db.select(models.User).order_by(models.User.name)
    ).scalars()
    return flask.render_template(
        "people.html",
        users=users,
    )


if __name__ == "__main__":
    app.run(debug=True)
