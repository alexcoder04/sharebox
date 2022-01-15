#!/usr/bin/env python3

import time
import os
from flask import Flask, render_template, send_file, request, redirect
from werkzeug.utils import secure_filename
import argparse

PORT = 8899
DELETE_AFTER = 60 * 5

app = Flask(__name__)

@app.route("/")
def index():
    files = []
    for f in os.listdir(app.config["SHARE_DIR"]):
        path = os.path.join(app.config["SHARE_DIR"], f)
        if not os.path.isfile(path):
            continue
        if os.path.getmtime(path) + DELETE_AFTER < time.time():
            os.remove(path)
            files.append({
                "name": f, "expires": 0, "deleted": True
                })
            continue
        files.append({
            "name": f, "expires": int(os.path.getmtime(path) + DELETE_AFTER - time.time()), "deleted": False
            })
    return render_template("index.html", files=files)

@app.route("/upload", methods=["POST"])
def upload():
    if "upload" not in request.files:
        return "ERROR"
    files = request.files.getlist("upload")
    for f in files:
        if f.filename is None:
            continue
        fname = secure_filename(f.filename)
        f.save(os.path.join(app.config["SHARE_DIR"], fname))
    return redirect(f"/?f={[i.filename for i in files]}")

@app.route("/dl/<path:file_path>")
def download(file_path):
    requested_file = os.path.abspath(os.path.join(app.config["SHARE_DIR"], file_path))
    if not requested_file.startswith(app.config["SHARE_DIR"]):
        return "ERROR"
    if not os.path.isfile(requested_file):
        return "ERROR"
    return send_file(requested_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="upload and download files"
            )

    parser.add_argument("--debug", action="store_true", help="run flask in debug mode")
    parser.add_argument("--share-dir", default="/media/share", type=str, help="folder to share")

    args = parser.parse_args()

    app.config["SHARE_DIR"] = args.share_dir

    app.run(port=PORT, debug=args.debug, host="0.0.0.0")

