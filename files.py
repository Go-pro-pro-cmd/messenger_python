import os
import datetime

def save_file(files, user_id, chat_id):
  
   
    saved_files = []
    i = 1

    folder = f"static/files/folder_{chat_id}"
    files_names = str(datetime.datetime.now()).replace(' ', '_').replace('.', ',')
    
    summ_files = len(files)
    os.makedirs(folder, exist_ok=True)
    for file in files:
            file_rash = file.filename.split('.')[1]
            filename = f"file_{i}_{summ_files}_{chat_id}_{user_id}_{files_names}.{file_rash}"
      
            file.save(os.path.join(folder, filename))
            saved_files.append(filename)
            i+=1
  
    
    return saved_files


