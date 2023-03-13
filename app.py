import cgi
import os
import re
from io import BytesIO
import openai
from chalice import Chalice

app = Chalice(app_name='annotaition')
app.api.binary_types.append('multipart/form-data')
openai.api_key = os.environ["OPENAI_API_KEY"]

@app.route('/', methods=['POST'], content_types=['multipart/form-data'], cors=True)
def index():
    try:
        body_binary = BytesIO(app.current_request.raw_body)
        environ = {'REQUEST_METHOD': 'POST'}
        headers = {'content-type': app.current_request.headers['content-type']}
        form = cgi.FieldStorage(fp=body_binary, environ=environ, headers=headers)

        if 'file' not in form or 'label' not in form:
            raise ValueError('Invalid request data')

        file_texts = form.getvalue('file').decode('utf-8').split("\n")
        target_labels = form.getvalue('label')

        return get_annotation_data(file_texts, target_labels)
    except Exception as e:
        return {'error': str(e)}

def get_annotation_data(file_texts, target_labels):
    response_data = []
    for text in file_texts:
        response = request_to_chatgpt(get_question(text, target_labels))
        response_text = response.choices[0]["message"]["content"].strip()
        label = extract_answer(r"ラベル:(.+)\n", response_text)
        reason = extract_answer(r"理由:(.+)\n", response_text)
        score = extract_answer(r"確信度:(.+)$", response_text)
        response_data.append(
            {
                "text": text,
                "label": label,
                "reason": reason,
                "score": score
            }
        )
    return response_data

def extract_answer(pattern, text):
    match = re.search(pattern, text)
    answer = ""
    if match:
        answer = match.group(1)
    return answer

def get_question(text, labels):
    question = f"""
    {text}

    上記の文章について、ラベルづけしてください。
    答えは{labels}のいずれかで答えてください。

    また、以下のフォーマットに従ってください。
    
    ラベル:○○
    理由:△△
    確信度:□□

    ○○には{labels}のいずれかを入れてください。
    △△にはラベルづけの理由を書いてください。
    □□にはそのラベルが正しいと思う度合いを0から100の数値で表してください。
    """
    return question

def request_to_chatgpt(question):
    return  openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": question},
        ],
    )
    return response
