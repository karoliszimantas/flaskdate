from app import app
from flask import render_template, url_for, request, send_from_directory
import csv
import os
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime
from time import mktime as mktime

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, "static/uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"csv"}
uploaded_file = ""


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if request.files["csvfile"] != "":
            global uploaded_file
            uploaded_file = request.files["csvfile"]
            if uploaded_file and allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                uploaded_file = uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], "user_file"))
        return render_template("menu.html")
    return render_template("home.html")


@app.route("/menu")
def info():
    return render_template("menu.html")


@app.route("/columns")
def columns():
    return render_template("columns.html")


@app.route("/all_columns")
def all_columns():
    df = pd.read_csv(UPLOAD_FOLDER + "/user_file", encoding='latin-1', error_bad_lines=False)
    return render_template("all_columns.html", df=df)


@app.route("/frows")
def frows():
    df = pd.read_csv(UPLOAD_FOLDER + "/user_file", encoding='latin-1', error_bad_lines=False)
    sample = df.head(5)
    html = sample.to_html()
    return render_template("frows.html", html=html)


@app.route("/lrows")
def lrows():
    df = pd.read_csv(UPLOAD_FOLDER + "/user_file", encoding='latin-1', error_bad_lines=False)
    sample = df.tail(5)
    html = sample.to_html()
    return render_template("lrows.html", html=html)


@app.route("/merge", methods=["GET", "POST"])
def merge():
    df = pd.read_csv(UPLOAD_FOLDER + "/user_file", encoding='latin-1', error_bad_lines=False)
    if request.method == "POST":
        column1 = request.form.get("column1")
        column2 = request.form.get("column2")
        column_name = request.form.get("name")
        if request.form.get("punct"):
            punct = request.form.get("punct")
            df[column_name] = df[column1].astype(str) + punct + df[column2].astype(str)
        else:
            df[column_name] = df[column1].astype(str) + df[column2].astype(str)
        df.to_csv("final_file.csv")
    return render_template("merge.html", df=df)


@app.route("/time")
def time():
    return render_template("time.html")


@app.route("/iso", methods=["GET", "POST"])
def iso():
    date_format = ""
    df = pd.read_csv(UPLOAD_FOLDER + "/user_file", encoding='latin-1', error_bad_lines=False)
    if request.method == "POST":
        if request.method == "POST":
            request_list = list(request.form.listvalues())
            new_list = [item for sublist in request_list for item in sublist]
            #unpacking list of received elements. Elements are packed within list
            for num in range(len(request_list) - 2):
                #request returns date format elements + punctuation mark, miliseconds and column elements. For iteration purposes (i.e. iterate through date format elements) 2 elements must be excluded
                if num == 0:
                    date_format += "%" + new_list[num]
                elif num < 3:
                    date_format += request.form.get("punc_date") + "%" + new_list[num]
                elif num == 3:
                    date_format += " " + "%" + new_list[num]
                elif num == 6:
                    date_format += ".%f"
                else:
                    date_format += request.form.get("punc_hour") + "%" + new_list[num]
            column = request.form.get("column")
            miliseconds = None
            if request.form.get("miliseconds"):
                #catching miliseconds element, i.e. if user entered miliseconds value
                miliseconds = int(request.form.get("miliseconds"))
            new_list = []
            iso = ""
            for value in df[column].values:
                value = str(value)
                try:
                    date_time_obj = datetime.strptime(value, date_format)
                    iso = date_time_obj.isoformat()
                    new_list.append(iso)
                except ValueError:
                    error_list = date_format.rsplit("%")
                    count = 0
                    for _ in error_list:
                        count += 1
                        try:
                            try_list = date_format.rsplit("%", count)
                            #catching 1 list from splitted lists and excluding last value (last value of date format string contains either punctuation mark or empty space
                            new_date_format = try_list[0][:-1]
                            date_time_obj = datetime.strptime(value, new_date_format)
                            iso = date_time_obj.isoformat()
                        except ValueError:
                            pass
                    if iso:
                        new_list.append(iso)
                    else:
                        new_list.append(None)
            df['Date_Iso'] = new_list
            df.to_csv("user_file.csv")
    return render_template("iso.html", df=df)


@app.route("/unix", methods=["GET", "POST"])
def unix():
    date_format = ""
    df = pd.read_csv(UPLOAD_FOLDER + "/user_file", encoding='latin-1', error_bad_lines=False)
    if request.method == "POST":
        if request.method == "POST":
            request_list = list(request.form.listvalues())
            new_list = [item for sublist in request_list for item in sublist]
            #unpacking list of received elements. Elements are packed within list
            for num in range(len(request_list) - 2):
                #request returns date format elements + punctuation mark, miliseconds and column elements. For iteration purposes (i.e. iterate through date format elements) 2 elements must be excluded
                if num == 0:
                    date_format += "%" + new_list[num]
                elif num < 3:
                    date_format += request.form.get("punc_date") + "%" + new_list[num]
                elif num == 3:
                    date_format += " " + "%" + new_list[num]
                elif num > 6:
                    date_format += ".%f"
                else:
                    date_format += request.form.get("punc_hour") + "%" + new_list[num]
            column = request.form.get("column")
            miliseconds = None
            if request.form.get("miliseconds"):
                #catching miliseconds element, i.e. if user entered miliseconds value
                miliseconds = int(request.form.get("miliseconds"))
            new_list = []
            unix = ""
            for values in df[column].values:
                values = str(values)
                try:
                    date_time_obj = datetime.strptime(values, date_format)
                    unix = time.mktime(date_time_obj.timetuple())
                    new_list.append(unix)
                except ValueError:
                    error_list = date_format.rsplit("%")
                    count = 0
                    for _ in error_list:
                        count += 1
                        try:
                            try_list = date_format.rsplit("%", count)
                            #catching 1 list from splitted lists and excluding last value (last value of date format string contains either punctuation mark or empty space
                            new_date_format = try_list[0][:-1]
                            date_time_obj = datetime.strptime(values, new_date_format)
                            unix = mktime(date_time_obj.timetuple())
                        except ValueError:
                            pass
                    if unix:
                        new_list.append(unix)
                    else:
                        new_list.append(None)
            df['Unix'] = new_list
            df.to_csv("user_file.csv")
    return render_template("unix.html", df=df)
