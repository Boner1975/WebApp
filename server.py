import os

from flask import Flask, render_template, url_for, request, redirect, abort, session
import bcrypt
import data_manager
import util

app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']
app.secret_key = 'mojsupersekretnyklucz'


@app.route("/")
def main_page():
    headers = ['id', 'submission_time', 'view_number', 'title', 'message', 'image', 'vote_number']
    questions = data_manager.display_five_latest_questions()
    return render_template("index.html", headers=headers, questions=questions, request=request)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/users")
def users():
    users_list_data = data_manager.users_list()
    return render_template("users.html", users_list_data=users_list_data)


@app.route("/list")
def display_question():
    headers = ['id', 'submission_time', 'view_number', 'title', 'message', 'image', 'vote_number']
    questions = data_manager.get_questions()
    header = request.cookies.get("Header")
    direction = request.cookies.get("Direction")
    questions = data_manager.sort_dictionaries(header, direction)

    return render_template("questions_list.html", headers=headers, questions=questions, request=request)


@app.route("/list/sort", methods=["POST"])
def sort_question_post():
    data = dict(request.form)
    direction = data["Direction"]
    header = data["Header"]
    questions = data_manager.sort_dictionaries(header, direction)
    response = redirect(url_for("display_question"))
    response.set_cookie("Direction", direction)
    response.set_cookie("Header", header)
    return response


@app.route("/question/<question_id>")
def question_page(question_id):
    data_manager.increment_view_number(question_id)
    question = data_manager.get_question(question_id)
    answers = data_manager.get_answers(question_id)
    comments = data_manager.get_comments(question_id)
    tag = data_manager.get_tags_by_question_id(question_id)
    dictionary_keys = []
    comments_keys = ['message', 'submission_time', 'edited_count']
    question_user_id = data_manager.get_user_id_by_question_id(question_id)
    session_user_id = data_manager.get_session_user_id(session['user_name'])
    if len(answers) > 0:
        dictionary_keys = answers[0].keys()
    return render_template("question_page.html", question=question, question_id=question_id,
                           answers=answers,  answers_keys=dictionary_keys, comments=comments,
                           comments_keys=comments_keys, tag=tag, question_user_id=question_user_id,
                           session_user_id=session_user_id)


@app.route("/list/add-question", methods=["GET"])
def add_question_get():
    return render_template("edit_question.html", question=None)


@app.route("/list/add-question", methods=["POST"])
def add_question_post():
    data = dict(request.form)
    data["id"] = data_manager.greatest_id()+1
    data["submission_time"] = data_manager.submission_time()
    data["view_number"] = 0
    data["vote_number"] = 0
    data["image"] = ""
    data["user_id"]= data_manager.get_session_user_id(session['user_name'])
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_ext = os.path.splitext(uploaded_file.filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        filename = str(data["id"]) + file_ext
        uploaded_file.save(os.path.join(util.IMAGES_DIR, filename))
        data["image"] = filename

    data_manager.add_question(data)

    return redirect(url_for("display_question"))


@app.route("/question/<question_id>/edit", methods=["GET"])
def edit_question_get(question_id):
    if not question_id.isnumeric():
        return redirect(url_for("display_question"))
    # question_id = int(question_id)
    question = data_manager.get_question(question_id)

    if question is None:
        return redirect(url_for('display_question'))

    return render_template("edit_question.html", question=question[0], question_id = question_id)


@app.route("/question/<question_id>/edit", methods=["POST"])
def edit_question_post(question_id):
    data = dict(request.form)

    data_manager.update_question(data)

    return redirect(url_for('display_question'))


@app.route("/question/<question_id>/delete")
def question_delete(question_id):
    data_manager.delete_question(question_id)
    return redirect(url_for("display_question"))


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def add_user_answer_post(question_id):
    if request.method == "POST":
        data = dict(request.form)
        data["id"] = data_manager.greatest_answer_id() + 1
        data["submission_time"] = data_manager.submission_time()
        data["view_number"] = 0
        data["vote_number"] = 0
        data['question_id'] = question_id
        data["image"] = ""
        data["user_id"] = data_manager.get_session_user_id(session['user_name'])
        data["accepted"] = False

        uploaded_file = request.files['image']
        if uploaded_file.filename != '':
            file_ext = os.path.splitext(uploaded_file.filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            filename = "a" + str(data["id"]) + file_ext
            uploaded_file.save(os.path.join(util.IMAGES_DIR, filename))
            data["image"] = filename

        data_manager.add_answer(data)
        return redirect(url_for("question_page", question_id=question_id))

    return render_template("answer.html", answer_id = 0, question_id=question_id, answer = None)


@app.route("/question/<question_id>/new-comment", methods=["GET", "POST"])
def add_comment_to_question(question_id):
    if request.method == "GET":
        return render_template("comment.html", question_id=question_id, comment=None)
    data = dict(request.form)
    data["id"] = data_manager.greatest_comment_id() + 1
    data["submission_time"] = data_manager.submission_time()
    data["answer_id"] = None
    data["edited_count"] = 0
    data['question_id'] = question_id
    data["user_id"] = data_manager.get_session_user_id(session['user_name'])
    data_manager.add_comment(data)
    return redirect(url_for("question_page", question_id=question_id))


@app.route("/comment/<comment_id>/edit", methods=["GET"])
def edit_comment_to_question(comment_id):

    comment = data_manager.get_comment(comment_id)

    return render_template("comment.html", comment=comment, comment_id=comment_id, question_id=comment["question_id"])


@app.route("/comment/<comment_id>/<question_id>/edit", methods=["POST"])
def edit_comment_to_question_post(comment_id, question_id):

    data = dict(request.form)
    data['submission_time'] = data_manager.submission_time()
    data['id'] = comment_id
    data['question_id'] = question_id
    data['answer_id'] = None
    data["edited_count"] = 0
    data_manager.update_comment(data)

    return redirect(url_for("question_page", question_id=question_id))


@app.route("/answer/<answer_id>/<question_id>/new-comment", methods=["GET", "POST"])
def add_comment_to_answer(answer_id, question_id):
    if request.method == "GET":
        return render_template("comment_answer.html", answer_id=answer_id, question_id=question_id, comment=None)
    data = dict(request.form)
    data["id"] = data_manager.greatest_comment_id() + 1
    data["submission_time"] = data_manager.submission_time()
    data["answer_id"] = answer_id
    data["edited_count"] = 0
    data['question_id'] = question_id
    data["user_id"] = data_manager.get_session_user_id(session['user_name'])
    data_manager.add_comment(data)
    return redirect(url_for("question_page", answer_id=answer_id, question_id=question_id))


@app.route("/comment/<comment_id>/edit", methods=["GET"])
def edit_comment_to_answer(comment_id):

    comment = data_manager.get_comment(comment_id)

    return render_template("comment_answer.html", comment=comment, comment_id=comment_id, answer_id=comment['answer_id'], question_id=comment["question_id"])


@app.route("/comment/<comment_id>/<answer_id>/<question_id>/edit", methods=["POST"])
def edit_comment_to_answer_post(comment_id, answer_id, question_id):

    data = dict(request.form)
    data['submission_time'] = data_manager.submission_time()
    data['id'] = comment_id
    data['question_id'] = question_id
    data['answer_id'] = data_manager.get_answer_id(question_id)
    data["edited_count"] = 0
    data_manager.update_comment(data)

    return redirect(url_for("question_page", answer_id=answer_id, question_id=question_id))


@app.route("/answer/<answer_id>/edit", methods=["GET"])
def edit_answer_get(answer_id):
    if not answer_id.isnumeric():
        return redirect(url_for("display_question"))
    answer = data_manager.get_answer(answer_id)

    if answer is None:
        return redirect(url_for('display_question'))

    return render_template("answer.html", answer=answer, answer_id = answer_id, question_id = answer["question_id"])


@app.route("/answer/<answer_id>/<question_id>/edit", methods=["POST"])
def edit_answer_post(answer_id, question_id):
    data = dict(request.form)

    data_manager.update_answer(data)

    return redirect(url_for("question_page", question_id=question_id))


@app.route("/question/<question_id>/answer/<answer_id>/delete")
def delete_answer(question_id, answer_id):
    data_manager.delete_answer(answer_id)
    return redirect(url_for("question_page", question_id=question_id))


@app.route("/question/<question_id>/comment/<comment_id>/delete")
def delete_comment(question_id, comment_id):
    data_manager.delete_comment(comment_id)
    return redirect(url_for("question_page", question_id=question_id))


@app.route("/question/<question_id>/vote_up")
def question_vote_up(question_id):
    data_manager.question_vote_up(question_id)
    return redirect(url_for("display_question"))


@app.route("/question/<question_id>/vote_down")
def question_vote_down(question_id):
    data_manager.question_vote_down(question_id)
    return redirect(url_for("display_question"))


@app.route("/answer/<answer_id>/<question_id>/vote_up")
def answer_vote_up(answer_id, question_id):
    data_manager.answer_vote_up(answer_id)
    return redirect(url_for("question_page", question_id=question_id))


@app.route("/answer/<answer_id>/<question_id>/vote_down")
def answer_vote_down(answer_id, question_id):
    data_manager.answer_vote_down(answer_id)
    return redirect(url_for("question_page", question_id=question_id))


@app.route("/search_question", methods=["GET", "POST"])
def search_question():
    search_phrase = request.args.get('search_phrase')
    search = data_manager.search_result(search_phrase)
    return render_template("search_result.html", search_phrase=search_phrase, search=search)


@app.route("/question/<question_id>/new-tag", methods=["GET", "POST"])
def add_tag_to_question(question_id):
    if request.method == "GET":
        tags=data_manager.get_all_tags()
        return render_template("tag.html", question_id=question_id, tag=None, tags=tags, message = "")
    data = dict(request.form)
    data["question_id"] = question_id

    if data["name"] == "" and data["name_select"] == "":
        tags = data_manager.get_all_tags()
        return render_template("tag.html", question_id=question_id, tag=None, tags=tags, message="You haven't choose any tag")
    elif data["name"] == "":
        data['name'] = data['name_select']
        param = data['name']
        data["tag_id"] = data_manager.get_tag_id_by_name(param)
        data_manager.add_tag(data)
    else:
        data['name'] = data['name']
        data["tag_id"] = data_manager.greatest_tag_id() + 1
        data["id"] = data_manager.greatest_tag_id() + 1
        data_manager.add_new_tag(data)
    return redirect(url_for("question_page", question_id=question_id))


@app.route("/question/<question_id>/tag/<tag_id>/delete")
def delete_tag(question_id, tag_id):
    data_manager.delete_tag(tag_id)
    return redirect(url_for("question_page", question_id=question_id))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template("registration.html")
    else:
        data = dict(request.form)
        users = data_manager.get_users()
        if data['user_name'] in [element['user_name'] for element in users]:
            return render_template("registration.html", message='This username already exist in database, choose another one')
        elif data['user_name'] == '' or data['password'] == '' or data['password1'] == '':
            return render_template("registration.html", message='Please fill in all fields')
        elif data['user_name'] != '' and data['password'] != data['password1']:
            return render_template("registration.html", message='Confirmation failed. Try again.')

        data['user_id'] = data_manager.greatest_user_id() + 1
        data['registration_date'] = data_manager.submission_time()
        data['reputation'] = 0
        data['password'] = hash_password(data['password'])[0].decode('utf_8')
        data_manager.add_user(data)
        return redirect(url_for("main_page"))


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('UTF-8'), salt)
    return hashed_password, salt

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        data = dict(request.form)
        users = data_manager.get_users()
        if request.form['user_name'] in [element['user_name'] for element in users] and verify_password(request.form['password'], data_manager.get_password(request.form['user_name'])):
            session['user_name'] = request.form['user_name']
            return redirect(url_for('main_page'))
        elif data['user_name'] == '' or data['password'] == '':
            return render_template("login.html", message='Please fill in all fields')
        else:
            message = 'Wrong password or username'

    return render_template('login.html', message=message)

def verify_password(plain_text_pswrd, hash_pswrd):
    #hashed_byte_password = hash_pswrd.encode('UTF-8')
    return bcrypt.checkpw(plain_text_pswrd.encode('UTF-8'), hash_pswrd)

@app.route('/logout')
def logout():
    session.pop('user_name', None)
    return redirect(url_for('main_page'))

def is_logged_in():
    return 'user_name' in session

@app.route("/tags")
def display_tags():
    tags_list= data_manager.display_tags()
    return render_template("tags.html", tags_list=tags_list)

@app.route("/answer/<answer_id>/<question_id>/accept_answer")
def accept_answer(answer_id, question_id):
    answer = data_manager.get_answer(answer_id)
    if answer['accepted'] == False:
        data_manager.accept_answer(answer_id)
    else:
        data_manager.remove_accept(answer_id)
    return redirect(url_for("question_page", question_id=question_id))


if __name__ == "__main__":
    app.run()
