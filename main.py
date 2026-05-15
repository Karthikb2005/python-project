from flask import Flask, render_template,request
import uuid
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    myid = uuid.uuid1()
    if request.method == "POST":
        print(request.files.keys()) #request means data coming from browser
        rec_id=request.form.get("uuid")
        desc=request.form.get("text")
        input_files=[]
        for key, value in request.files.items(): 
            print(key, value)
            # Upload File
            file=request.files[key]
            if file:
                filename = secure_filename(file.filename)
                if(not(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],    rec_id)))): 
                    os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], rec_id))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], rec_id,filename))
                input_files.append(file.filename)
            #Capture the description and save it to a file 
            with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, "desc.txt"), "w") as f:
              f.write(desc)
        for fl in input_files:
            with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id,"input.txt"),"a") as f:
                f.write(f"file '{fl}'\nduration 1\n")
                
            
            
    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    reels = os.listdir("static/reels")
    print(reels)
    return render_template("gallery.html", reels=reels)

import threading
import time
import subprocess
from text_to_audio import text_to_speech_file

def background_worker():
    """Background thread to process videos automatically"""
    while True:
        try:
            if not os.path.exists("done.txt"):
                with open("done.txt", "w") as f: pass
                
            with open("done.txt", "r") as f:
                done_folders = [line.strip() for line in f.readlines()]
            
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
            folders = os.listdir(UPLOAD_FOLDER)
            for folder in folders:
                if folder not in done_folders:
                    print(f"Processing folder: {folder}")
                    # 1. Text to Audio
                    desc_path = os.path.join(UPLOAD_FOLDER, folder, "desc.txt")
                    if os.path.exists(desc_path):
                        with open(desc_path, "r") as f:
                            text = f.read()
                        text_to_speech_file(text, folder)
                        
                        # 2. Create Reel (FFmpeg)
                        os.makedirs("static/reels", exist_ok=True)
                        command = [
                            'ffmpeg', '-f', 'concat', '-safe', '0',
                            '-i', f'user_uploads/{folder}/input.txt',
                            '-i', f'user_uploads/{folder}/audio.mp3',
                            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black',
                            '-c:v', 'libx264', '-c:a', 'aac', '-shortest',
                            '-r', '30', '-pix_fmt', 'yuv420p', '-y',
                            f'static/reels/{folder}.mp4'
                        ]
                        subprocess.run(command, check=True)
                        
                        # 3. Mark as done
                        with open("done.txt", "a") as f:
                            f.write(folder + "\n")
                        print(f"Finished processing: {folder}")
        except Exception as e:
            print(f"Error in background worker: {e}")
        
        time.sleep(5)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static/reels", exist_ok=True)

# Start the background generator thread
threading.Thread(target=background_worker, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
