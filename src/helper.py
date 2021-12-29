import re
from quantiphy import Quantity
import mimetypes
from flask import url_for
from datetime import datetime
from .explorer import validate_node, get_breadcrumbs, path_to_url, mimeicon

class Validator():
    email_regex = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

       
    def email(self, field):
        if re.match(self.email_regex, field):
            return True
        return False
    
    def password(self, field):
        if re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", field):
            return True
        return False
    
    def phone(self, field):
        if re.match(r"^\d{10}$", field):
            return True
        return False
    
class Helper():
    def iterate(self, node, root, folder=True):
        l = []
        for this in node.iterdir():
            path = path_to_url(this, anchor=root)
            link = url_for("explorer.sub", node=path)
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
            print(this.name, path, link, icon, size, type_, cdate)
            dir_dict = {"name" : this.name, "path" : path, "link" : link, "icon" : icon, "size" : size, "type" : type_, "cdate" : cdate}
            l.append(dir_dict)
        return l
    
    def get_info(self, this, root):
        path = path_to_url(this, anchor=root)
        link = url_for("explorer.sub", node=path)
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
            return None
        cdate = datetime.utcfromtimestamp(stat.st_ctime).strftime(
            "%Y/%m/%d %H:%M:%S"
        )
        print(this.name, path, link, icon, size, type_, cdate)
        dir_dict = {"name" : this.name, "path" : path, "link" : link, "icon" : icon, "size" : size, "type" : type_, "cdate" : cdate}
        return dir_dict
        
        