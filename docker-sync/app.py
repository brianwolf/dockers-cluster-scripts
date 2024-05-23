import logging
import os
import subprocess
import time

import requests

# ================================================
# CONFIGS
# ================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s (%(process)d) - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ================================================
# VARS
# ================================================

GIT_CLONE_PATH = os.environ["GIT_CLONE_PATH"]
GIT_USER = os.environ["GIT_USER"]
GIT_TOKEN = os.environ["GIT_TOKEN"]
GIT_REPO_NAME = os.environ["GIT_REPO_NAME"]
GIT_BRANCH = os.environ["GIT_BRANCH"]
TIME_SECONDS_CHECK = float(os.environ["TIME_SECONDS_CHECK"])

LAST_COMMIT_SHA = None
TIME_SECONDS_WAIT_UP_DOCKERS = 5

# ================================================
# METHODS
# ================================================


def sh(cmd: str, echo: bool = False) -> str:

    if echo:
        logging.info(cmd)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    p.wait()
    return p.stdout.read().decode()


def get_last_commit_sha() -> str:

    headers = {"Authorization": f"Bearer {GIT_TOKEN}"}
    url = f"https://api.github.com/repos/{GIT_USER}/{GIT_REPO_NAME}/commits"

    return requests.get(url, headers=headers).json()[0]["sha"]


def clone_repository(
    repo: str, user: str, password: str, branch: str, path: str
) -> str:

    git_repo_url_full = f"https://{user}:{password}@github.com/{user}/{repo}.git"

    sh(f"rm -fr {GIT_CLONE_PATH}")
    sh(f"git clone -c http.sslVerify=false -b {branch} {git_repo_url_full} {path}")


def get_docker_compose_paths_list(base_path: str) -> list[str]:

    result = []
    for dirpath, _, files in os.walk(base_path):

        result.extend(
            [
                f"{dirpath}/{file}"
                for file in files
                if file.endswith(".yaml") or file.endswith(".yml")
            ]
        )

    return result


def down_docker_compose(path: str):

    compose_paths_files = get_docker_compose_paths_list(path)

    for compose_path_file in compose_paths_files:

        compose_name = compose_path_file.split("/")[-2]

        sh(
            f"cd {os.path.join(path, compose_name)} && docker compose down --remove-orphans"
        )


def up_docker_compose(path: str):

    compose_paths_files = get_docker_compose_paths_list(path)

    for compose_path_file in compose_paths_files:

        compose_name = compose_path_file.split("/")[-2]

        logging.info("------------------------------------------------")
        logging.info(f">> {compose_name} <<")
        logging.info(f"File: {compose_path_file}")
        logging.info("------------------------------------------------")

        sh(
            f"cd {os.path.join(path, compose_name)} && docker compose pull && docker compose up -d"
        )


# ================================================
# SCRIPT
# ================================================

while True:

    commit_sha = get_last_commit_sha()

    if LAST_COMMIT_SHA == commit_sha:
        time.sleep(TIME_SECONDS_CHECK)
        continue

    LAST_COMMIT_SHA = commit_sha

    if os.path.exists(GIT_CLONE_PATH):
        down_docker_compose(GIT_CLONE_PATH)
        time.sleep(TIME_SECONDS_WAIT_UP_DOCKERS)

    clone_repository(GIT_REPO_NAME, GIT_USER, GIT_TOKEN, GIT_BRANCH, GIT_CLONE_PATH)

    up_docker_compose(GIT_CLONE_PATH)
