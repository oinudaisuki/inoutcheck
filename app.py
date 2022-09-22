import os
from flask import Flask, render_template, request, redirect, url_for, make_response
import inoutcheck as inout
import zipfile
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'result'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
ROOT = app.root_path

app.config['UPLOAD_FOLDER'] = os.path.join(ROOT, UPLOAD_FOLDER)
app.config['RESULT_FOLDER'] = os.path.join(ROOT, RESULT_FOLDER)

# 拡張子確認
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 初期表示
@app.route('/')
def home():
    return render_template('inoutcheck.html', title='check flex', message='')

# アップロードファイル保存
@app.route('/', methods=['POST'])
def file_upload():
    files = request.files.getlist('file')

    for file in files:
        if file.filename == '':
            return render_template('inoutcheck.html', title='check flex', message='ファイルを選択してください')

        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    return redirect(url_for('file_download'))


# ファイルダウンロード
@app.route('/download/', methods=['GET'])

def file_download():
    resultfilenames = innout_check()
    filearr = ','.join(resultfilenames)

    filearr = filearr.split(',')
    response = make_response()

    if len(filearr) == 1:
        # CSV単体
        response.data = open(os.path.join(app.config['RESULT_FOLDER'], filearr[0] + '.csv'), 'rb').read()
        response.headers['Content-type'] = 'text/csv'
        response.headers['Content-Disposition'] = ('attachment; filename="' + filearr[0] + '.csv"').encode('utf_8')

    else:
        # ZIP生成
        with zipfile.ZipFile(
            os.path.join(app.config['RESULT_FOLDER'], 'archive_zipfile.zip'), 'w',
            compression=zipfile.ZIP_DEFLATED) as zf:

            for filename in filearr:
                zf.write(os.path.join(app.config['RESULT_FOLDER'], filename + '.csv'), arcname=filename + '.csv')

        response.data = open(os.path.join(app.config['RESULT_FOLDER'], 'archive_zipfile.zip'), 'rb').read()
        response.headers['Content-type'] = 'application/zip'
        response.headers['Content-Disposition'] = ('attachment; filename="archive_zipfile.zip"').encode('utf_8')

    return response

# 実行
def innout_check():
    return inout.innoutcheck()


if __name__ == "__main__":
    #app.run()
    app.run(debug=True, port=5000, host='0.0.0.0')