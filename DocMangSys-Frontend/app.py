from flask import Flask, render_template, request, redirect, url_for, send_file # type: ignore
import requests # type: ignore

app = Flask(__name__)
API_URL = "http://127.0.0.1:8000"  # FastAPI URL

@app.route('/')
def index():
    response = requests.get(f"{API_URL}/documents")
    documents = response.json()
    return render_template("index.html", documents=documents)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = {'file': request.files['file']}
        data = {
            'title': request.form['title'],
            'content': request.form['content']
        }
        response = requests.post(f"{API_URL}/documents", data=data, files=files)
        return redirect(url_for('index'))
    return render_template("upload.html")

@app.route('/view/<int:doc_id>')
def view(doc_id):
    response = requests.get(f"{API_URL}/documents/{doc_id}")
    document = response.json()
    return render_template("view.html", doc=document)

@app.route('/download/<int:doc_id>')
def download(doc_id):
    response = requests.get(f"{API_URL}/documents/{doc_id}/download", stream=True)
    filename = response.headers.get('content-disposition').split('filename=')[1]
    return send_file(response.raw, as_attachment=True, download_name=filename)

@app.route('/delete/<int:doc_id>')
def delete(doc_id):
    requests.delete(f"{API_URL}/documents/{doc_id}")
    return redirect(url_for('index'))

@app.route('/update/<int:doc_id>', methods=['GET', 'POST'])
def update(doc_id):
    if request.method == 'POST':
        data = {
            'title': request.form['title'],
            'content': request.form['content']
        }
        files = {}
        if 'file' in request.files and request.files['file'].filename != '':
            files['file'] = request.files['file']
        response = requests.put(f"{API_URL}/documents/{doc_id}", data=data, files=files or None)
        return redirect(url_for('index'))

    document = requests.get(f"{API_URL}/documents/{doc_id}").json()
    return render_template("update.html", doc=document)

if __name__ == '__main__':
    app.run(debug=True)
