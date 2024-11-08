import logging
import os
import subprocess
import sys
import time

import requests

# ================================================
# VARS
# ================================================

GIT_REPO_URL = "https://github.com/brianwolf/dockers-cluster.git"
GIT_REPO_BRANCH = "main"
GIT_USER = "brianwolf"
GIT_TOKEN = os.environ["GIT_TOKEN"]

TIME_SECONDS_WAIT_UP_DOCKERS = 5
WORKINDIR = "/tmp/docker-sync"
GIT_CLONE_PATH = f"{WORKINDIR}/repo"
GIT_COMMIT_SHA_PATH = f"{WORKINDIR}/commit-sha.txt"

# ================================================
# CONFIGS
# ================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s (%(process)d) - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)

# ================================================
# METHODS
# ================================================


def sh(cmd: str, echo: bool = False) -> str:

    if echo:
        logging.info(cmd)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    p.wait()
    return p.stdout.read().decode()


def get_repo_name() -> str:

    return GIT_REPO_URL.replace('https://', '').replace('http://', '').split('/')[2].replace('.git', '')


def get_last_git_commit_sha() -> str:

    headers = {"Authorization": f"Bearer {GIT_TOKEN}"}
    url = f"https://api.github.com/repos/{GIT_USER}/{get_repo_name()}/commits"

    return requests.get(url, headers=headers).json()[0]["sha"]


def clone_repository() -> str:

    git_repo_url_full = f"https://{GIT_USER}:{GIT_TOKEN}@{GIT_REPO_URL.replace('https://', '').replace('http://', '')}"

    sh(f"rm -fr {GIT_CLONE_PATH}")
    sh(f"git clone -c http.sslVerify=false -b {GIT_REPO_BRANCH} {git_repo_url_full} {GIT_CLONE_PATH}")


def get_docker_compose_paths_list() -> list[str]:

    return [
        f"{GIT_CLONE_PATH}/{d}/docker-compose.yaml"
        for d in os.listdir(GIT_CLONE_PATH)
        if os.path.isdir(d) and d not in [".git", "img"]
    ]


def down_docker_compose():

    for compose_path_file in get_docker_compose_paths_list():

        compose_name = compose_path_file.split("/")[-2]

        logging.info(f"Downing compose {compose_name}")
        sh(
            f"cd {os.path.join(GIT_CLONE_PATH, compose_name)} && docker compose down --remove-orphans"
        )


def up_docker_compose():

    for compose_path_file in get_docker_compose_paths_list():

        compose_name = compose_path_file.split("/")[-2]

        logging.info("------------------------------------------------")
        logging.info(f">> {compose_name} <<")
        logging.info(f"File: {compose_path_file}")
        logging.info("------------------------------------------------")

        sh(
            f"cd {os.path.join(GIT_CLONE_PATH, compose_name)} && docker compose down --remove-orphans && docker compose pull && docker compose up -d"
        )


# ================================================
# SCRIPT
# ================================================

if not os.path.exists(WORKINDIR):
    sh(f"mkdir -p {WORKINDIR}")

if not os.path.exists(GIT_COMMIT_SHA_PATH):
    sh(f"touch {GIT_COMMIT_SHA_PATH}")

local_commit_sha = open(GIT_COMMIT_SHA_PATH, 'r').read()
git_commit_sha = get_last_git_commit_sha()

if local_commit_sha != git_commit_sha:

    if os.path.exists(GIT_CLONE_PATH):
        down_docker_compose()
        time.sleep(TIME_SECONDS_WAIT_UP_DOCKERS)

    clone_repository()
    up_docker_compose()

    open(GIT_COMMIT_SHA_PATH, 'w').write(git_commit_sha)
