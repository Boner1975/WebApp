from datetime import datetime
from connection import *
import time
import os
import util
from typing import List, Dict

from psycopg2 import sql
from psycopg2.extras import RealDictCursor, RealDictRow, DictCursor
from psycopg2.extensions import AsIs

import connection


@connection.connection_handler
def users_list(cursor: RealDictCursor):
    query = """
    SELECT user_name, registration_date, count_of_asked_questions, count_of_answers, count_of_comments, reputation
    FROM users
    ORDER BY reputation 
    """

    cursor.execute(query)
    return cursor.fetchall()



@connection.connection_handler
def search_result(cursor: RealDictCursor, search_phrase):
    query = """
    SELECT question.title FROM question
    WHERE LOWER(question.title)  LIKE LOWER(%(search_phrase)s)
    UNION
    SELECT question.message FROM question
    WHERE LOWER(question.message)  LIKE LOWER(%(search_phrase)s)
    UNION
    SELECT answer.message FROM answer
    WHERE LOWER(answer.message)  LIKE LOWER(%(search_phrase)s)
    UNION
    SELECT comment.message FROM comment
    WHERE LOWER(comment.message)  LIKE LOWER(%(search_phrase)s)
    """
    # query = """
    # SELECT  question.title, question.message, answer.message, comment.message
    # FROM  answer, question, comment
    # WHERE question.title LIKE %(search_phrase)s
    # OR question.message LIKE %(search_phrase)s
    # OR answer.message LIKE %(search_phrase)s
    # OR comment.message LIKE %(search_phrase)s
    # """

    param = {'search_phrase': '%' + search_phrase + '%'}
    cursor.execute(query, param)
    return cursor.fetchall()


@connection.connection_handler
def get_dictionary_keys(cursor: RealDictCursor):
    query = """
        SELECT column_name
        FROM INFORMATION_SCHEMA.columns
        WHERE table_name = N'question'"""
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_questions(cursor: RealDictCursor):
    query = """
        SELECT id, submission_time, view_number, title, message, image, vote_number
        FROM question
        ORDER BY submission_time desc"""
    cursor.execute(query)
    return cursor.fetchall()


def submission_time():
    return datetime.today().replace(microsecond=0)
#zwracany typ danych to datetime.datetime


@connection.connection_handler
def get_question(cursor: RealDictCursor, question_id):
    query = """
        SELECT title, message, COALESCE(image,'') image
        FROM question
        WHERE id = %(question_id)s"""
    param = {'question_id': question_id}
    cursor.execute(query, param)
    return cursor.fetchall()


@connection.connection_handler
def get_answers(cursor: RealDictCursor, question_id):
    query = """
        SELECT id, message ,COALESCE(image,'') image, vote_number
        FROM answer
        WHERE question_id = %(question_id)s
        ORDER BY submission_time"""
    param = {'question_id': question_id}
    cursor.execute(query, param)
    return cursor.fetchall()

@connection.connection_handler
def get_comments(cursor: RealDictCursor, question_id):
    query = """
        SELECT submission_time, message, id, answer_id, edited_count
        FROM comment
        WHERE question_id = %(question_id)s
        ORDER BY submission_time"""
    param = {'question_id': question_id}
    cursor.execute(query, param)
    return cursor.fetchall()

@connection.connection_handler
def get_comment(cursor: RealDictCursor, comment_id):
    query = """
        SELECT id, question_id, answer_id, message, submission_time, edited_count
        FROM comment
        WHERE id = %(comment_id)s
        ORDER BY submission_time"""
    param = {'comment_id': comment_id}
    cursor.execute(query, param)
    comments = cursor.fetchall()
    if len(comments) == 0:
        return None
    return comments[0]


@connection.connection_handler
def get_answer(cursor: RealDictCursor, answer_id):
    query = """
        SELECT id, message ,COALESCE(image,'') image, vote_number, question_id
        FROM answer
        WHERE id = %(answer_id)s
        ORDER BY submission_time"""
    param = {'answer_id': answer_id}
    cursor.execute(query, param)

    answers = cursor.fetchall()

    if len(answers) == 0:
        return None
    return answers[0]

@connection.connection_handler
def greatest_id(cursor: RealDictCursor):
    query = """
    SELECT MAX(id) id
    FROM question
    """

    cursor.execute(query)
    result = cursor.fetchall()
    return result[0]['id']


@connection.connection_handler
def greatest_answer_id(cursor: RealDictCursor):
    query = """
        SELECT id
        FROM answer
        ORDER BY id DESC 
        LIMIT 1
        """

    cursor.execute(query)
    result = cursor.fetchall()
    return result[0]['id']

@connection.connection_handler
def greatest_comment_id(cursor: RealDictCursor):
    query = """
        SELECT id
        FROM comment
        ORDER BY id DESC 
        LIMIT 1
        """
    cursor.execute(query)
    result = cursor.fetchall()
    return result[0]['id']

@connection.connection_handler
def greatest_tag_id(cursor: RealDictCursor):
    query = """
        SELECT id
        FROM tag
        ORDER BY id DESC 
        LIMIT 1
        """
    cursor.execute(query)
    result = cursor.fetchall()
    return result[0]['id']

@connection.connection_handler
def greatest_question_tag_id(cursor: RealDictCursor):
    query = """
        SELECT question_id
        FROM question_tag
        ORDER BY question_id DESC 
        LIMIT 1
        """
    cursor.execute(query)
    result = cursor.fetchall()
    return result[0]['id']

@connection.connection_handler
def greatest_user_id(cursor: RealDictCursor):
    query = """
        SELECT user_id
        FROM users
        ORDER BY user_id DESC 
        LIMIT 1
        """
    cursor.execute(query)
    result = cursor.fetchall()
    if len(result) == 0:
        return 0
    else:
        return result[0]['user_id']

@connection.connection_handler
def get_answer_id(cursor: RealDictCursor, question_id):
    query = """
        SELECT answer_id
        FROM comment
        WHERE id = %(question_id)s
        """
    param = {'question_id': question_id}
    cursor.execute(query, param)
    result = cursor.fetchall()
    return result[0]['answer_id']

@connection.connection_handler
def add_comment(cursor: RealDictCursor, comment) -> list:
    comment_id = greatest_comment_id()
    command = """
    INSERT INTO comment (id, question_id, answer_id, message, submission_time, edited_count)
    VALUES (%(id)s, %(question_id)s, %(answer_id)s, %(message)s, %(submission_time)s, %(edited_count)s)
    """

    param = {
        'id': comment['id'],
        'question_id': comment['question_id'],
        'answer_id': comment['answer_id'],
        'message': comment['message'],
        'submission_time': comment['submission_time'],
        'edited_count': comment['edited_count']
    }
    cursor.execute(command, param)

@connection.connection_handler
def add_answer(cursor: RealDictCursor, answer) -> list:
    answer_id = greatest_answer_id()
    command = """
    INSERT INTO answer (id, submission_time, vote_number, question_id, message, image)
    VALUES (%(id)s, %(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s, %(image)s)
    """

    param = {
        'id': answer['id'],
        'submission_time': answer['submission_time'],
        'vote_number': answer['vote_number'],
        'question_id': answer['question_id'],
        'message': answer['message'],
        'image': answer['image']
    }
    cursor.execute(command, param)

@connection.connection_handler
def update_answer(cursor: RealDictCursor, data):
    command = """ UPDATE answer
    SET message = %(message)s
    WHERE id = %(answer_id)s"""
    param = {
        'answer_id': data['id'],
        'message': data['message']
    }
    cursor.execute(command, param)

@connection.connection_handler
def add_question(cursor: RealDictCursor, question) -> list:
    command = """
    INSERT INTO question (id, submission_time, view_number, vote_number, title, message, image)
    VALUES (%(id)s, %(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s);"""


    param = {
        'id': question['id'],
        'submission_time': question['submission_time'],
        'view_number': question['view_number'],
        'vote_number': question['vote_number'],
        'title': question['title'],
        'message': question['message'],
        'image': question['image']
    }
    cursor.execute(command, param)

@connection.connection_handler
def update_question(cursor: RealDictCursor, data):
    command = """ UPDATE question
    SET 
        title = %(title)s,
        message = %(message)s
    WHERE id = %(question_id)s"""
    param = {
        'question_id': data['id'],
        'title': data['title'],
        'message': data['message']
    }
    cursor.execute(command, param)


@connection.connection_handler
def update_comment(cursor: RealDictCursor, data):
    command = """ UPDATE comment
    SET 
        submission_time = %(submission_time)s,
        message = %(message)s,
        edited_count = edited_count + 1
    WHERE id = %(comment_id)s"""
    param = {
        'submission_time': data['submission_time'],
        'comment_id': data['id'],
        'message': data['message']
    }
    cursor.execute(command, param)

@connection.connection_handler
def delete_question(cursor: RealDictCursor, question_id):
    query = """
            DELETE FROM comment
            WHERE question_id = %(question_id)s;
            DELETE FROM answer
            WHERE question_id = %(question_id)s;
            DELETE FROM question_tag
            WHERE question_id = %(question_id)s;
            DELETE FROM question
            WHERE id = %(question_id)s"""

    param = {'question_id': question_id}
    cursor.execute(query, param)


@connection.connection_handler
def delete_answer(cursor: RealDictCursor, answer_id):
    query = """
    DELETE FROM comment
    WHERE answer_id = %(answer_id)s;    
    DELETE FROM answer
    WHERE id = %(answer_id)s"""

    param = {'answer_id': answer_id}
    cursor.execute(query, param)

@connection.connection_handler
def delete_comment(cursor: RealDictCursor, comment_id):
    query = """
    DELETE FROM comment
    WHERE id = %(comment_id)s"""

    param = {'comment_id': comment_id}
    cursor.execute(query, param)


@connection.connection_handler
def question_vote_up(cursor: RealDictCursor, question_id):
    query = """
        UPDATE question
        SET vote_number = vote_number + 1
        WHERE id = %(question_id)s"""

    param = {'question_id': question_id}
    cursor.execute(query, param)


@connection.connection_handler
def question_vote_down(cursor: RealDictCursor, question_id):
    query = """
        UPDATE question
        SET vote_number = vote_number - 1
        WHERE id = %(question_id)s"""

    param = {'question_id': question_id}
    cursor.execute(query, param)


@connection.connection_handler
def answer_vote_up(cursor: RealDictCursor, answer_id):
    query = """
    UPDATE answer
    SET vote_number = vote_number + 1
    WHERE id = %(answer_id)s"""

    param = {'answer_id': answer_id}
    cursor.execute(query, param)


@connection.connection_handler
def answer_vote_down(cursor: RealDictCursor, answer_id):
    query = """
        UPDATE answer
        SET vote_number = vote_number - 1
        WHERE id = %(answer_id)s"""

    param = {'answer_id': answer_id}
    cursor.execute(query, param)

@connection.connection_handler
def display_five_latest_questions(cursor: RealDictCursor):
    query = """
        SELECT id, submission_time, view_number, title, message, image, vote_number
        FROM question
        ORDER BY submission_time desc
        LIMIT 5"""
    cursor.execute(query)
    return cursor.fetchall()

@connection.connection_handler
def add_tag(cursor: RealDictCursor, tag) -> list:
    command = """
    INSERT INTO question_tag (question_id, tag_id)
    VALUES (%(question_id)s, %(tag_id)s)
    ON CONFLICT do nothing 
    """

    param = {
        'tag_id': tag['tag_id'],
        'name': tag['name'],
        'question_id':tag['question_id'],
    }
    cursor.execute(command, param)


@connection.connection_handler
def add_new_tag(cursor: RealDictCursor, tag) -> list:
    command = """
    INSERT INTO tag (id, name)
    VALUES (%(id)s, %(name)s);
    
    INSERT INTO question_tag (question_id, tag_id)
    VALUES (%(question_id)s, %(tag_id)s)
    """

    param = {
        'tag_id': tag['tag_id'],
        'id': tag['id'],
        'name': tag['name'],
        'question_id': tag['question_id']
    }
    cursor.execute(command, param)


@connection.connection_handler
def get_tag_id_by_name(cursor: RealDictCursor, parameter):
    query = """
        SELECT id
        FROM tag
        WHERE tag.name = %(parameter)s"""
    param = {"parameter": parameter}
    cursor.execute(query, param)
    result = cursor.fetchall()
    return result[0]['id']

@connection.connection_handler
def get_tags_by_question_id(cursor: RealDictCursor, question_id):
    query = """
        SELECT id, name
        FROM tag, question_tag
        WHERE tag.id = question_tag.tag_id AND question_id=%(question_id)s"""
    param = {"question_id" : question_id}
    cursor.execute(query, param)
    return cursor.fetchall()

@connection.connection_handler
def get_all_tags(cursor: RealDictCursor):
    query = """
        SELECT name
        FROM tag"""
    cursor.execute(query)
    return cursor.fetchall()

@connection.connection_handler
def delete_tag(cursor: RealDictCursor, tag_id):
    query = """
            DELETE FROM question_tag
            WHERE tag_id = %(tag_id)s;
"""

    param = {'tag_id': tag_id}
    cursor.execute(query, param)

@connection.connection_handler
def increment_view_number(cursor: RealDictCursor, question_id):
    query="""
            UPDATE question
            SET view_number = view_number + 1
            WHERE id = %(question_id)s"""
    param = {'question_id': question_id}
    cursor.execute(query, param)

@connection.connection_handler
def sort_dictionaries(cursor: RealDictCursor, header, direction):
    query = """
        SELECT id, submission_time, view_number, title, message, image, vote_number
        FROM question"""
    cursor.execute(query)
    questions = cursor.fetchall()
    return util.sort_dictionaries(questions, header, direction)

@connection.connection_handler
def get_users(cursor: RealDictCursor):
    query = """
        SELECT user_name
        FROM users"""
    cursor.execute(query)
    return cursor.fetchall()

@connection.connection_handler
def add_user(cursor: RealDictCursor, user) -> list:
    command = """
    INSERT INTO users (user_id, user_name, registration_date, count_of_asked_questions, count_of_answers,
                count_of_comments, reputation, password)
    VALUES (%(user_id)s, %(user_name)s, %(registration_date)s, %(count_of_asked_questions)s, %(count_of_answers)s, 
            %(count_of_comments)s, %(reputation)s, %(password)s);"""

    param = {
        'user_id': user['user_id'],
        'user_name': user['user_name'],
        'registration_date': user['registration_date'],
        'count_of_asked_questions': user['count_of_asked_questions'],
        'count_of_answers': user['count_of_answers'],
        'count_of_comments': user['count_of_comments'],
        'reputation': user['reputation'],
        'password': user['password']
    }
    cursor.execute(command, param)

@connection.connection_handler
def get_users(cursor: RealDictCursor):
    query = """
        SELECT user_name
        FROM users"""
    cursor.execute(query)
    return cursor.fetchall()

@connection.connection_handler
def get_password(cursor: RealDictCursor, username):
    query = """
        SELECT password
        FROM users
        where users.user_name = %(username)s"""
    param = {"username": username}
    cursor.execute(query, param)
    result = cursor.fetchall()
    return bytes(result[0]['password'], 'utf_8')

