#!/usr/bin/env python3
#        _                        _            ___  _  _   
#   __ _| | _____  _____ ___   __| | ___ _ __ / _ \| || |  
#  / _` | |/ _ \ \/ / __/ _ \ / _` |/ _ \ '__| | | | || |_ 
# | (_| | |  __/>  < (_| (_) | (_| |  __/ |  | |_| |__   _|
#  \__,_|_|\___/_/\_\___\___/ \__,_|\___|_|   \___/   |_|  
# 
# Copyright (c) 2021 alexcoder04 <https://github.com/alexcoder04>
# 
# sharebox - upload and download files over http
# requires: flask, werkzeug, argparse
# 

import time
import os
from flask import Flask, render_template, send_file, request, redirect
from werkzeug.utils import secure_filename
import argparse

app = Flask(__name__)

# main page, files overview
@app.route("/")
def index():
    files = []
    for f in os.listdir(app.config["SHARE_DIR"]):
        path = os.path.join(app.config["SHARE_DIR"], f)
        delete_after = app.config["KEEP"]
        if not os.path.isfile(path):
            continue
        if os.path.getmtime(path) + delete_after < time.time():
            os.remove(path)
            files.append({
                "name": f,
                "expires": 0,
                "deleted": True
                })
            continue
        files.append({
            "name": f,
            "expires": int(os.path.getmtime(path) + delete_after - time.time()),
            "deleted": False
            })
    return render_template("index.html", files=files)

# upload file via http post
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

# download file
@app.route("/dl/<path:file_path>")
def download(file_path):
    requested_file = os.path.abspath(os.path.join(app.config["SHARE_DIR"], file_path))
    if not requested_file.startswith(app.config["SHARE_DIR"]):
        return "ERROR"
    if not os.path.isfile(requested_file):
        return "ERROR"
    return send_file(requested_file)

# ifmain
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="upload and download files"
            )

    parser.add_argument("--debug", action="store_true", help="run flask in debug mode")
    parser.add_argument("--share-dir", default="/media/share", type=str, help="folder to share")
    parser.add_argument("--keep", default=(60*5), type=int, help="deleted files after so many seconds")
    parser.add_argument("--port", default=8899, type=int, help="port to listen on")

    args = parser.parse_args()

    app.config["SHARE_DIR"] = args.share_dir
    app.config["KEEP"] = args.keep

    app.run(port=args.port, debug=args.debug, host="0.0.0.0")

