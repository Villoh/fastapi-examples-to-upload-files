import httpx
import time

url_stream ='http://127.0.0.1:8000/upload_stream'
url_shutil='http://127.0.0.1:8000/upload_shutil'
url_shutil_threadpool='http://127.0.0.1:8000/upload_shutil_threadpool'
upload_aiofiles_chunks='http://127.0.0.1:8000/upload_aiofiles_chunks'
url_aiofiles='http://127.0.0.1:8000/upload_aiofiles'
url_standard_sync='http://127.0.0.1:8000/upload_standard_sync'
url_standard_async='http://127.0.0.1:8000/upload_standard_async'

files = {'file': open('dummy.pdf', 'rb')}
headers={'Filename': 'dummy.pdf'}
data = {'data': 'Hello World!'}

with httpx.Client() as client:
    start = time.time()
    r = client.post(url_shutil_threadpool, data=data, files=files, headers=headers)
    end = time.time()
    print(f'Time elapsed: {end - start}s')
    print(r.status_code, r.json(), sep=' ')