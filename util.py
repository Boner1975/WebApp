IMAGES_DIR = "static/uploaded"

def sort_dictionaries(questions, header, direction):
    if direction == "ascending" and header != "":
        if header == "view_number" or header == "vote_number":
            questions.sort(key=lambda x: int(x[header]))
        elif header == 'submission_time':
            questions.sort(key=lambda x: (x["submission_time"]))
        else:
            questions.sort(key=lambda x: (x[header].lower()))
    elif direction == "descending" and header != "":
        if header == "view_number" or header == "vote_number":
            questions.sort(key=lambda x: int(x[header]), reverse=True)
        elif header == 'submission_time':
            questions.sort(key=lambda x: (x["submission_time"]), reverse=True)
        else:
            questions.sort(key=lambda x: (x[header].lower()), reverse=True)
    else:
        questions.sort(key=lambda x: (x["submission_time"]), reverse=True)

    return questions
