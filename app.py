from flask import Flask, request, render_template, redirect, send_from_directory, url_for, flash
import os
import shutil

app = Flask(__name__)

app.secret_key = '31413243214234'
# Папка, куда будут загружаться файлы (замени путь на свой)
UPLOAD_FOLDER = r'C:\Users\aleks\PycharmProjects\Flask_Folders_for_teachers\Materials'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Главная страница: просмотр папок и создание новых
@app.route('/', methods=['GET', 'POST'])
def index():
    # Получаем список папок в корневой директории
    folders = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if
               os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], f))]

    if request.method == 'POST':
        # Создание новой папки
        new_folder = request.form.get('folder_name')
        if new_folder:
            new_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], new_folder)
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            return redirect(url_for('index'))

    return render_template('index.html', folders=folders)


# Просмотр содержимого папки
@app.route('/folder/<folder_name>', methods=['GET', 'POST'])
def folder_contents(folder_name):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    if os.path.exists(folder_path):
        files = os.listdir(folder_path)

        if request.method == 'POST':
            new_folder_name = request.form.get('folder_name')
            if new_folder_name:
                new_folder_path = os.path.join(folder_path, new_folder_name)
                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)

        return render_template('folder.html', folder_name=folder_name, files=files)
    else:
        return f"Folder {folder_name} does not exist", 404


# Удаление папки
@app.route('/delete_folder/<folder_name>', methods=['POST'])
def delete_folder(folder_name):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)  # Удаляем папку и все ее содержимое
            flash(f'Папка "{folder_name}" успешно удалена.')
        except OSError as e:
            flash(f'Ошибка при удалении папки "{folder_name}": {e}')
    else:
        flash(f'Папка "{folder_name}" не найдена.')
    return redirect(url_for('index'))


# Загрузка файлов
@app.route('/upload/<folder_name>', methods=['GET', 'POST'])
def upload_file(folder_name):
    if request.method == 'POST':
        # Проверяем, есть ли файл в запросе
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'

        # Сохраняем файл в указанную папку
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file.save(os.path.join(folder_path, file.filename))
        return redirect(url_for('folder_contents', folder_name=folder_name))

    return render_template('upload.html', folder_name=folder_name)


# Скачивание файлов
@app.route('/download/<folder_name>/<filename>')
def download_file(folder_name, filename):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    return send_from_directory(folder_path, filename, as_attachment=True)


# Удаление файла или папки
@app.route('/delete_file/<folder_name>/<filename>', methods=['POST'])
def delete_file(folder_name, filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name, filename)

    if os.path.exists(file_path):
        if os.path.isfile(file_path):  # Если это файл, удаляем файл
            os.remove(file_path)
            flash(f'Файл "{filename}" успешно удален.')
        elif os.path.isdir(file_path):  # Если это папка, удаляем папку и её содержимое
            try:
                shutil.rmtree(file_path)
                flash(f'Папка "{filename}" успешно удалена.')
            except OSError as e:
                flash(f'Ошибка при удалении папки "{filename}": {e}')
        else:
            flash(f'"{file_path}" не является файлом или папкой.')
    else:
        flash(f'Файл или папка "{filename}" не найдены.')

    return redirect(url_for('folder_contents', folder_name=folder_name))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
