# Example to upload files in FastAPI using [streaming-form-data](https://github.com/siddhantgoel/streaming-form-data) to upload files.

This is a small example which you can try to upload files to a web server using FastAPI.

Improveemnts of up to **x4 times faster** can be observed when uploading files using `streaming-form-data` with respect to `shutil` or other native methods.

## Where I found this solution?
Thanks to Chris for providing the [FastAPI solution](https://stackoverflow.com/a/73443824), as well as the context and explanation. 

## Results
#### Using shutil
![alt text](results/shutil.png)

#### Using [streaming-form-data](https://github.com/siddhantgoel/streaming-form-data)
![alt text](results/streaming-form-data.png)