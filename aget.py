#!/usr/bin/python3

import argparse
import requests

from gitlab import *

def download_artifact(url, token, project_id, build_id, filename="artifacts.zip"):
    '''

    :type filename: str
    :type project_id: int or str
    :type build_id: int or str
    :return: downloaded file name
    '''
    token_params = {"PRIVATE-TOKEN": token}

    url = "{url}/api/v3/projects/{project_id}/builds/{build_id}/artifacts".format(build_id=build_id, project_id=project_id, url=url)
    responce = requests.get(url, headers=token_params, stream=True)
    with open(filename, 'wb') as f:
        for chunk in responce.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return filename

def retry_build(url, token, project_id, build_id):
    '''

    :type filename: str
    :type project_id: int or str
    :type build_id: int or str
    :return: downloaded file name
    '''
    token_params = {"PRIVATE-TOKEN": token}

    url = "{url}/api/v3/projects/{project_id}/builds/{build_id}/retry".format(build_id=build_id, project_id=project_id, url=url)
    responce = requests.post(url, headers=token_params, stream=True)
    print(responce)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Download artifacts from gitlab repository')
    parser.add_argument("--url", nargs=1, type=str)
    parser.add_argument('--token', nargs=1, help="token to access GitLab's api")
    parser.add_argument("--project", nargs=1, type=str)
    parser.add_argument("--branch", nargs=1, type=str)
    parser.add_argument("--op", nargs=1, type=str)


    args = parser.parse_args()
    branch_name = args.branch[0]
    token = args.token[0]
    url = args.url[0]
    project_id = args.project[0] # type: str
    project_id = project_id.replace("/", "%2F")

    rebuild = False
    if args.op[0] == "rebuild":
        rebuild = True

    gl = Gitlab(url, token)


    branches = gl.project_branches.list(project_id=project_id)
    for branch in branches: # type: ProjectBranch
        if branch_name == branch.as_dict()["name"]:
            commit_sha = branch.as_dict()['commit']["id"]
            commit_manager = gl.project_commits # type: ProjectCommitManager
            commit = commit_manager.get(commit_sha, project_id=project_id) # type: ProjectCommit
            for build in commit.builds(): # type: ProjectBuild
                build_dict = build.as_dict()
                if rebuild:
                    retry_build(url, token, project_id, build.as_dict()["id"])
                    exit(0)
                else:
                    if build_dict["status"] == "success" and "artifacts_file" in build_dict:
                        filename = download_artifact(url, token, project_id, build.as_dict()["id"])
                        print(filename)
                        exit(0)
    exit(-1)






