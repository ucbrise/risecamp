import json
import os

import git
import requests
import configparser
from ground import GroundClient


def get_commits(git_repo, latest_nodes):
    parents_log = git_repo.log('--all',
                               '--format="%H,%P"')  # log with commit hash and parent hashes
    parents_log = parents_log.replace("\"", "").split("\n")
    parents_log = [row.strip().split(",") for row in parents_log]
    parents_log[-1:] = [[parents_log[-1:][0][0], ""]]  # fix for first commit
    parents_log = [[row[0], row[1].split()] for row in parents_log]
    source_log = git_repo.log('--all', '--source',
                              '--format=oneline')  # log with source branch of commit
    source_log = source_log.split("\n")
    source_log = [[row.split("\t")[0], row.split("\t")[1].split(" ")[0]] for row in source_log]

    for c_hash, node in latest_nodes.items():  # remove commits from before the latest commit
        for item in source_log:
            if c_hash == item[0]:
                source_log = source_log[:source_log.index(item)]
        for item in parents_log:
            if c_hash == item[0]:
                parents_log = parents_log[:parents_log.index(item)]

    source_log = [[row[1]] for row in source_log]
    fields = ['branch', 'commitHash', 'parentHashes']
    commits_dict = list(zip(source_log, parents_log))
    commits_dict = [[row[0][0], row[1][0], row[1][1]] for row in list(commits_dict)]
    commits_dict = [dict(zip(fields, row)) for row in commits_dict]
    return commits_dict


def post_commits(commits, latest_nodes, repo_name, node_id):
    node_ids = {}

    for c in reversed(commits):
        parents = c['parentHashes']
        parent_nodes = []
        for parent in parents:
            parent_nodes.append(node_ids[parent])

        tags = {
            "branch": {
                "key": "branch",
                "value": c['branch'],
                "type": "string"
            },
            "commit": {
                "key": "commit",
                "value": c['commitHash'],
                "type": "string"
            },
        }

        nv_id = gc.create_node_version(node_id, tags, parent_nodes)['id']
        node_ids[c['commitHash']] = nv_id

        print('Commit added to ground: ' + c['commitHash'])


config = configparser.ConfigParser()
config.read('config.ini')

gc = GroundClient()

def add_repo(repo_name):
    # create URLS for API interaction
    gitUrl = "https://github.com/" + repo_name

    repo = git.Repo.init('/tmp/' + repo_name, bare=True)
    origin = repo.create_remote('origin', url=gitUrl)

    class MyProgressPrinter(git.RemoteProgress):
        def update(self, op_code, cur_count, max_count=None, message=''):
            print(op_code, cur_count, max_count, cur_count / (max_count or 100.0),
                  message or "NO MESSAGE")
            # end

    print('fetching commits...')
    for fetch_info in repo.remotes.origin.fetch(progress=MyProgressPrinter()):
        print("Updated %s to %s" % (fetch_info.ref, fetch_info.commit))
    print('commits fetched!')

    g = git.Git('/tmp/' + repo_name)
    node_id = gc.create_node(repo_name, repo_name)['id']
    print(node_id)

    repo_commits = get_commits(g, {})  # Get a list of the latest commits
    post_commits(repo_commits, {}, repo_name, node_id)
