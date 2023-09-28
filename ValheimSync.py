import time

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from progress.bar import Bar
import os

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

file_paths = []


def prepare(get_path: str):
    work_path = get_path
    file_paths.clear()
    for dirs, folder, files in os.walk(work_path):
        for file in files:
            file_paths.append(os.path.join(dirs, file))


def upload_files() -> str:
    try:
        drive = GoogleDrive(gauth)

        file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

        print("Предварительная очистка:")
        bar = Bar('Processing', max=len(file_list))
        for file1 in file_list:
            file1.Delete()
            bar.next()
        bar.finish()

        bar = Bar('Processing', max=len(file_paths))
        print("Выгрузка данных:")
        for cur_file in file_paths:
            file_name = cur_file.split("\\")[len(cur_file.split("\\")) - 1]
            if file_name[:3] == 'Alv':
                my_file = drive.CreateFile({'title': f'{file_name}'})
                my_file.SetContentFile(cur_file)
                my_file.Upload()

            bar.next()
        bar.finish()
        return 'Успешно'
    except Exception as _ex:
        return 'Что-то пошло не так'


def download_files(get_path: str) -> None:
    drive = GoogleDrive(gauth)

    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

    bar = Bar('Processing', max=len(file_list))
    print("Обновление данных:")
    for file1 in file_list:
        cur_file = get_path + file1['title']
        downloaded_file = drive.CreateFile({'id': file1['id']})
        downloaded_file.GetContentFile(cur_file)
        bar.next()
    bar.finish()


exit_stat = False

while not exit_stat:
    command = input()
    try:
        command_parts = command.split()
        if command_parts[0] == 'path':
            path = command_parts[1]
            print(path)
            if not os.path.exists(os.getcwd() + "/file_with_path.txt"):
                file_with_path = open(os.getcwd() + "/file_with_path.txt", "w")
                file_with_path.write(path)
            else:
                print("Путь уже установлен")
        elif command == 'save':
            try:
                path = open('file_with_path.txt', "r")
                send_path = path.read()
                prepare(send_path)
                upload_files()
            except FileNotFoundError:
                print("Сначала задай путь до папки с сохранением")
        elif command == 'update':
            try:
                path = open('file_with_path.txt', "r")
                send_path = path.read()
                prepare(send_path)
                download_files(send_path)
            except FileNotFoundError:
                print("Сначала задай путь до папки с сохранением")
        elif command == 'exit':
            break
        else:
            pass
    except ValueError:
        print("Сука, читай инструкцию")
