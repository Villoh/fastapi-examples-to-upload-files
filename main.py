import shutil
from fastapi import FastAPI, Header, Request, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from streaming_form_data.validators import MaxSizeValidator
import streaming_form_data
from starlette.requests import ClientDisconnect
import aiofiles
import os

MAX_FILE_SIZE = 1024 * 1024 * 1024 * 4  # = 4GB
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024
CHUNK_SIZE = 1024 * 1024

app = FastAPI()

class MaxBodySizeException(Exception):
    def __init__(self, body_len: str):
        self.body_len = body_len

class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.body_len = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes):
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=self.body_len)
        

# standard sync
@app.post('/upload_standard_sync')
def upload_standard(file: UploadFile):
    with open(f'./files/{file.filename}', 'wb') as writer:
        writer.write(file.file.read())
    return {"message": f"Successfuly uploaded {file.filename}"}

# standard async
@app.post('/upload_standard_async')
async def upload_standard_async(file: UploadFile):
    with open(f'./files/{file.filename}', 'wb') as writer:
        # Read a file in chunks and write it to the buffer.
        while True:
            chunk = await file.read() 
            if not chunk:
                break
            writer.write(chunk)
    return {"message": f"Successfuly uploaded {file.filename}"}

# shutil
@app.post('/upload_shutil')
def upload_shutil(file: UploadFile):
    with open(f'./files/{file.filename}', 'wb') as writer:
        shutil.copyfileobj(file.file, writer)
    return {"message": f"Successfuly uploaded {file.filename}"}

# shutil threadpool
@app.post("/upload_shutil_threadpool")
async def upload(file: UploadFile):
    try:
        writer = await run_in_threadpool(open, file.filename, 'wb')
        await run_in_threadpool(shutil.copyfileobj, file.file, writer)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        if 'writer' in locals(): await run_in_threadpool(writer.close)
        await file.close()
    return {"message": f"Successfuly uploaded {file.filename}"}

# aiofiles
@app.post('/upload_aiofiles')
async def upload_standard(file: UploadFile):
    contents = await file.read()
    async with aiofiles.open(f'./files/{file.filename}', 'wb') as writer:
                await writer.write(contents)
    return {"message": f"Successfuly uploaded {file.filename}"}

# aiofiles chunks
@app.post('/upload_aiofiles_chunks')
async def upload_standard(file: UploadFile):
    async with aiofiles.open(f'./files/{file.filename}', 'wb') as writer:
            while chunk := await file.read(CHUNK_SIZE):
                await writer.write(chunk)
    return {"message": f"Successfuly uploaded {file.filename}"}
 
# stream library
@app.post('/upload_stream')
async def upload(request: Request):
    body_validator = MaxBodySizeValidator(MAX_REQUEST_BODY_SIZE)
    filename = request.headers.get('Filename')
    
    if not filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail='Filename header is missing')
    try:
        filepath = os.path.join('./files/', os.path.basename(filename)) 
        file_ = FileTarget(filepath, validator=MaxSizeValidator(MAX_FILE_SIZE))
        data = ValueTarget()
        parser = StreamingFormDataParser(headers=request.headers)
        parser.register('file', file_)
        parser.register('data', data)
        
        async for chunk in request.stream():
            body_validator(chunk)
            parser.data_received(chunk)
    except ClientDisconnect:
        print("Client Disconnected")
    except MaxBodySizeException as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
           detail=f'Maximum request body size limit ({MAX_REQUEST_BODY_SIZE} bytes) exceeded ({e.body_len} bytes read)')
    except streaming_form_data.validators.ValidationError:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
            detail=f'Maximum file size limit ({MAX_FILE_SIZE} bytes) exceeded') 
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='There was an error uploading the file') 
   
    if not file_.multipart_filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='File is missing')

    print(data.value.decode())
    print(file_.multipart_filename)
        
    return {"message": f"Successfuly uploaded {filename}"}