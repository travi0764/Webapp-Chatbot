import os
from utils.logger import logging
from routers.updateData import update
from fastapi.responses import JSONResponse
from typing import List
from fastapi import UploadFile

from concurrent.futures import ThreadPoolExecutor

def processUploads(files: List[UploadFile]):
    try:
        # Check if the "uploads" directory exists, create it if not
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # List to store unique and latest file paths
        unique_files = []

        for uploaded_file in files:
            if uploaded_file.filename != '':
                # Check if the file with the same name already exists in the "uploads" directory
                file_path = os.path.join(upload_dir, uploaded_file.filename)
                if os.path.exists(file_path):
                    # File already exists, skip saving
                    continue

                # Save the unique file in the "uploads" directory
                with open(file_path, 'wb') as file:
                    file.write(uploaded_file.file.read())
                    logging.info('File successfully saved in local upload directory.')

                unique_files.append(file_path)
        # print(f'Printing length of unique files {len(unique_files)}')
        if unique_files:
            # Process the unique and latest files using the update function
            try:
                with ThreadPoolExecutor() as executor:
                    executor.map(update, unique_files)

                return {'message': 'Files successfully uploaded and processed.'}
            except Exception as e:
                return {"error" : str(e)}
        else:

            return {'message': 'No new files to upload.'}

    except Exception as e:
        logging.info(f'Inside upload data function in app.py {e}')
        return JSONResponse(content={'error': str(e)}, status_code=500)
