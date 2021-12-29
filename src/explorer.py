import pathlib
from collections import namedtuple
import contextlib
from datetime import datetime
from re import L
import shutil
from functools import lru_cache
import mimetypes
import sys

from quantiphy import Quantity
from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    send_file,
    abort,
    redirect,
    jsonify,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

explorer = Blueprint("explorer", __name__)
FileInfo = namedtuple("FileInfo", "name path link icon size type cdate")
Breadcrumb = namedtuple("Breadcrumb", "name link")
mimeicon = {
    "application": "microsoft-windows",
    "audio": "music",
    "font": "format-font",
    "image": "image-outline",
    "text": "text",
    "video": "video-outline",
}


def path_to_url(path, anchor=None):
    """Return a url path made from parts in this path"""
    if anchor is not None:
        path = path.relative_to(anchor)
    return "/".join(path.parts)


def get_breadcrumbs(path, root):
    """Returns a list of Breadcrumb objects for this path"""
    parents = path.relative_to(root).parents
    links = map(path_to_url, parents)
    crumbs = []
    for par, lnk in zip(parents, links):
        name = par.name
        # hiding the root folder name from user
        if not name:
            name = "Home"
        url = url_for("explorer.sub", node=lnk)
        crumbs.append(Breadcrumb(name, url))
    return reversed(crumbs)

@explorer.route("/explorer/<path:node>", endpoint="sub")
@explorer.route("/explorer/", defaults={"node": None})
@explorer.route("/explorer", defaults={"node": None})
@login_required
def traverse(node):
    """Returns the contents of each folder"""
    # get parameters
       
    print (node)
    # get parameters
    attach = request.args.get("attach") or False
    print (attach)
    node = validate_node(node, (root := current_user.directory))

    # this path does not exist
    if not node.exists():
        abort(404)

    # this is a folder
    if node.is_dir():
        table = []
        for this in node.iterdir():
            path = path_to_url(this, anchor=root)
            link = url_for("explorer.sub", node=path)
            print ('>', link)
            stat = this.stat()
            if this.is_dir():
                type_ = "DIR"
                size = ""
                icon = "folder-outline"
            elif this.is_file():
                mime = mimetypes.guess_type(this)[0]
                if mime is not None:
                    icon = mimeicon[mime.split("/")[0]]
                else:
                    icon = "file-question-outline"
                type_ = this.suffix.upper()
                size = Quantity(this.stat().st_size, "B").binary()
            else:
                continue
            cdate = datetime.utcfromtimestamp(stat.st_ctime).strftime(
                "%Y/%m/%d %H:%M:%S"
            )
            row = FileInfo(this.name, path, link, icon, size, type_, cdate)
            table.append(row)
        if node == pathlib.Path(root):
            directory = "Home"
            icon = "folder-account-outline"
        else:
            directory = node.name
            icon = "folder-open-outline"
        print ('GET THIS', node, root)
        return render_template(
            "explorer.html",
            directory=directory,
            locale=path_to_url(node, anchor=root),
            breadcrumb=get_breadcrumbs(node, root),
            icon=icon,
            table=table,
        )

    # if it's a file send the content to the user
    elif node.is_file():
        if attach:
            return send_file(node, as_attachment=True)
        else:
            return send_file(node)


@explorer.post("/mkdir/<path:node>")
@explorer.post("/mkdir/", defaults={"node": None})
@login_required
def mkdir(node):
    """Make a sub-folder in this folder"""
    name = request.form.get("directory")

    # this prevents relative paths in folder names
    if "./" in name or ".\\" in name:
        abort(404)

    node = validate_node(node, root := current_user.directory)
    new = validate_node(name, node)
    with contextlib.suppress(FileNotFoundError):
        new.mkdir(exist_ok=True)
        return redirect(url_for("explorer.sub", node=path_to_url(new, anchor=root)))
    abort(404)


@explorer.post("/delete")
@login_required
def delete():
    """Delete items from the explorer"""
    print (">TREE" , request.json)
    for node in request.json:
        node = validate_node(node, root := current_user.directory)
        if not node.exists():
            continue
        if node == pathlib.Path(root):
            continue
        if node.is_dir():
            shutil.rmtree(node)
        elif node.is_file():
            node.unlink()
    return jsonify(success=True)



@explorer.post("/upload/<path:node>")
@explorer.post("/upload/", defaults={"node": None})
@login_required
def upload(node):
    """Upload file to this folder"""
    node = validate_node(node, current_user.directory)
    resp = []
    for key, f in request.files.items():
        # if the user has not selected a file, we will get an empty filename
        if f.filename:
            name = secure_filename(f.filename)
            new = validate_node(name, node)
            f.save(new)
            resp.append({"filename": f.filename})
    return jsonify(resp)


@lru_cache(maxsize=32)
def validate_node(node, root, from_init=False) -> pathlib.Path:
    """Ensure that node is a child of root"""
    if isinstance(node, str):
        node = node.strip()
    root = pathlib.Path(root)
    if node is None:
        return root
    # empty string for node is an error
    if not node:
        if from_init:
            return None
        abort(404, "Invalid Filename")
    node = pathlib.Path(node)
    if node.is_absolute():
        if from_init:
            return None
        abort(404, "Invalid Filename")
    node = root / node
    # https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.is_relative_to
    with contextlib.suppress(ValueError):
        node.relative_to(root)
        return node
    if from_init:
        return None
    abort(404, "Invalid Filename")
