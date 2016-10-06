#  -*- coding: utf-8 -*-
from flask import request, render_template

from operator import itemgetter
from aktiv_gitlab import AktivGitlab
from app import app
from config import *
from common import console
from os import path
from shutil import rmtree
from core import Core


@app.route("/", methods=["POST", "GET"])
def index():
    try:
        gitlab = AktivGitlab(GITLAB_SERVER, token=GITLAB_TOKEN)
    except Exception as e:
        return render_template("error_page.html", error_info=[e])
    projects_name = [project["path"] for project in gitlab.get_projects()]
    projects_name.sort()
    return render_template("index.html", projects_name=projects_name)


# TODO : add code to Core class
@app.route("/merge", methods=["POST"])
def merge():
    try:
        gitlab = AktivGitlab(GITLAB_SERVER, token=GITLAB_TOKEN)
    except Exception as e:
        return render_template("error_page.html", error_info=[e])

    project_id = request.form.keys()[0]
    mr_id = request.form.values()[0]

    mr_info = gitlab.get_mr_by_id(project_id, mr_id)
    message = []
    message.append("Title: {0}".format(mr_info["title"]))
    message.append("From \"{0}\" to \"{1}\"".format(mr_info["source_branch"], mr_info["target_branch"]))
    message.append("Author: {0}".format(mr_info["author"]["name"]))
    message.append("______________________________________________")
    message.append("Commands: ")

    project_name = gitlab.get_project_name_by_id(project_id)
    project_info = gitlab.get_project(project_name)
    ssh_url_to_repo = project_info["ssh_url_to_repo"]

    if path.exists(project_name):
        rmtree(project_name)

    commands = []
    commands.append("git clone {0} {1}".format(ssh_url_to_repo, project_name))
    commands.append("git -C {0} rebase origin/{1} {2}".format(project_name, mr_info["source_branch"], mr_info["target_branch"]))
    commands.append("git -C {0} merge origin/{1} {2}".format(project_name, mr_info["source_branch"], mr_info["target_branch"]))
    commands.append("git -C {0} push origin {1}:{1}".format(project_name, mr_info["target_branch"]))

    for command in commands:
        try:
            res = console(command)
            if res["code"] != 0:
                raise Exception("[ERROR]: command {0} failed".format(command))
            else:
                message.append(command)
        except Exception as e:
            message.append(e)
            return render_template("error_page.html", error_info=message)

    if path.exists(project_name):
        rmtree(project_name)

    message.append("______________________________________________")
    message.append("Merge Request #{0} was closed".format(mr_id))
    return render_template("info_page.html", title="Git info", message_info=message)


# TODO : add code to Core class
@app.route("/mr_info", methods=["POST"])
def merge_info():
    try:
        project_name = request.form["project_name"]
        gitlab = AktivGitlab(GITLAB_SERVER, token=GITLAB_TOKEN)
        mr = gitlab.get_mr_by_project(request.form["project_name"])
    except Exception as e:
        return render_template("error_page.html", error_info=[e])

    if not mr:
        error_info = ["Can not find MR in {0} project".format(request.form["project_name"])]
        return render_template("error_page.html", error_info=error_info)

    for m in mr:
        emojy = gitlab.get_emojy(m["project_id"], m["id"])
        counter_thumbsup = 0
        for e in emojy:
            if e["name"] == "thumbsup":
                counter_thumbsup += 1
        if counter_thumbsup < 2 and (m["merge_status"] == "can_be_merged") and not m["work_in_progress"]:
            m["merge_status"] = "Not enough approve"
    return render_template("mr_info.html", title=project_name, mr_data=sorted(mr, key=itemgetter('merge_status')))


@app.route("/help_page", methods=["POST", "GET"])
def help():
    return render_template("help.html", title="Help")
