# backend/services/file_utils.py

def classify_file(filename):
    """
    Classifies a file as 'code', 'binary', or 'other' based on its extension.
    """
    extension = filename.lower().split('.')[-1]
    code_exts = {'py', 'java', 'c', 'cpp', 'js', 'ts', 'html', 'css'}
    binary_exts = {'pdf', 'jpg', 'jpeg', 'png', 'docx'}

    if extension in code_exts:
        return 'code'
    elif extension in binary_exts:
        return 'binary'
    else:
        return 'other'
