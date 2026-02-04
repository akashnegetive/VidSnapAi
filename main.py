from flask import Flask, render_template, request
import uuid
from werkzeug.utils import secure_filename
import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "user_uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -------------------------
# EXTENSION CHECK
# -------------------------
def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------
# IMAGE VALIDATION + FIX
# -------------------------
def normalize_image(path):
    try:
        img = Image.open(path).convert("RGB")
        img.save(path, "JPEG")
        return True
    except Exception as e:
        print(f"[IMG] invalid image {path}: {e}")
        return False


# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
@app.route("/create", methods=["GET","POST"])
def create():
    myid = uuid.uuid1()
    created = False   # ⭐ flag

    if request.method == "POST":
        print("[CREATE] method =", request.method)
        rec_id = str(uuid.uuid4())
        print("[CREATE] NEW JOB:", rec_id)
        desc = request.form.get("text")

        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
        os.makedirs(upload_path, exist_ok=True)
        print("[CREATE] upload_path =", upload_path)
        print("[CREATE] exists =", os.path.exists(upload_path))
        print("[CREATE] parent list =", os.listdir(os.path.dirname(upload_path)))


        input_files = []

        for key in request.files:
            file = request.files[key]
            if file and file.filename != "":
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_path, filename))
                input_files.append(filename)

        with open(os.path.join(upload_path, "desc.txt"), "w", encoding="utf-8") as f:
            f.write(desc or "")

        with open(os.path.join(upload_path, "input.txt"), "w") as f:
            for fl in input_files:
                f.write(f"file '{os.path.abspath(os.path.join(upload_path, fl))}'\n")
                f.write("duration 1\n")

        created = True   # ⭐ mark success

    return render_template("create.html", myid=myid, created=created)



# -------------------------
@app.route("/gallery")
def gallery():
    try:
        reels_path = "static/reels"
        os.makedirs(reels_path, exist_ok=True)
    
        reels = os.listdir(reels_path)
        return render_template("gallery.html", reels=reels)
    except Exception as e:
        print("[GALLERY ERROR]", e)
        return "Gallery temp error", 500


# -------------------------
if __name__ == "__main__":
    import os, threading
    from generate_process import run_worker_loop

    threading.Thread(target=run_worker_loop, daemon=True).start()

    port = int(os.getenv("PORT", 9000))
    app.run(host="0.0.0.0", port=port)








