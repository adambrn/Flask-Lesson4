import os
import sys
import time
import requests
import threading
import multiprocessing
import asyncio
import aiohttp
import argparse

def download_image(url, output_folder, prefix=""):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            file_name = os.path.join(output_folder, f"{prefix}{os.path.basename(url)}")
            with open(file_name, 'wb') as file:
                file.write(response.content)
            return file_name
        else:
            print(f"Не удалось загрузить изображение с {url}")
    except Exception as e:
        print(f"Ошибка при загрузке изображения с {url}: {e}")
    return None

def process_url_thread(url, output_folder):
    start_time = time.time()
    file_name = download_image(url, output_folder, prefix="threading_")
    end_time = time.time()
    if file_name:
        print(f"Изображение {file_name} загружено за {end_time - start_time:.2f} секунд")

def process_url_process(url, output_folder):
    process_start = time.time()
    file_name = download_image(url, output_folder, prefix="multiprocessing_")
    process_end = time.time()
    if file_name:
        print(f"Изображение {file_name} загружено за {process_end - process_start:.2f} секунд")

async def download_image_async(url, session, output_folder):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                start_time = time.time()
                file_name = os.path.join(output_folder, f"asyncio_{os.path.basename(url)}")
                with open(file_name, 'wb') as file:
                    file.write(await response.read())
                end_time = time.time()
                print(f"Изображение {file_name} загружено за {end_time - start_time:.2f} секунд")
                return file_name
            else:
                print(f"Не удалось загрузить изображение с {url}")
    except Exception as e:
        print(f"Ошибка при загрузке изображения с {url}: {e}")
    return None

async def process_urls_async(urls, output_folder):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(download_image_async(url, session, output_folder))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Загрузка изображений с разными методами")
    parser.add_argument("output_folder", nargs="?", default="", help="Папка для сохранения изображений (по умолчанию - папка скрипта)")
    parser.add_argument("urls", nargs="*", default=[], help="Список URL-адресов для загрузки (необязательно)")
    args = parser.parse_args()

    output_folder = args.output_folder
    if not output_folder:
        output_folder = os.path.dirname(os.path.abspath(__file__))

    if not args.urls:
        default_urls = [
            "https://images.wallpaperscraft.ru/image/single/list_zelenyj_makro_1015853_1920x1080.jpg",
            "https://img2.akspic.ru/attachments/crops/0/3/3/1/7/171330/171330-voda-priroda-zemlya-derevo-vodoem-3840x2160.jpg",
            "https://w.forfun.com/fetch/d7/d7da5336cdec973bb1dc28fc4ad0f93a.jpeg",
        ]
        args.urls = default_urls

    thread_pool = []
    for url in args.urls:
        thread = threading.Thread(target=process_url_thread, args=(url, output_folder))
        thread_pool.append(thread)
        thread.start()
    for thread in thread_pool:
        thread.join()

    process_pool = []
    for url in args.urls:
        process = multiprocessing.Process(target=process_url_process, args=(url, output_folder))
        process_pool.append(process)
        process.start()
    for process in process_pool:
        process.join()

    loop = asyncio.get_event_loop()
    tasks = process_urls_async(args.urls, output_folder)
    loop.run_until_complete(tasks)
