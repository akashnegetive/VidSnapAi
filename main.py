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

@app.route("/create",methods=["GET","POST"])
def create():
    myid = uuid.uuid1()
    if request.method == "POST":
        rec_id = request.form.get("uuid")
        desc = request.form.get("text")

        # ✅ Create folder first
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
        os.makedirs(upload_path, exist_ok=True)

        input_files = []

        # ✅ Save uploaded files
        for key, value in request.files.items():
            file = request.files[key]
            if file and file.filename != "":
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_path, filename))
                input_files.append(filename)

        # ✅ Save description text
        with open(os.path.join(upload_path, "desc.txt"), "w", encoding="utf-8") as f:
            f.write(desc or "")

        # ✅ Create input.txt for ffmpeg
        input_txt_path = os.path.join(upload_path, "input.txt")
        with open(input_txt_path, "w", encoding="utf-8") as f:
            for fl in input_files:
                f.write(f"file '{fl}'\nduration 1\n")

        print(f"[UPLOAD] Created folder: {upload_path}")
        print(f"[UPLOAD] Files: {input_files}")

    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    reels=os.listdir("static/reels")
    print(reels)
    return render_template("gallery.html",reels=reels)

app.run(debug=True)