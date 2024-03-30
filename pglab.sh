#!/bin/bash
set -m

setup_environment() {
    sudo apt-get update && \
    sudo apt-get install -y \
        wget \
        build-essential \
        libreadline-dev \
        zlib1g-dev \
        flex \
        bison \
        libxml2-dev \
        libxslt1-dev \
        libssl-dev \
        libperl-dev \
        git \
        bash \
        python3 \
        python3-pip \
        python3-venv \
        libipc-run-perl \
        libfuse-dev \

    sudo modprobe fuse
}

concat_paths() {
    local path1="$1"
    local path2="$2"

    # Remove trailing slash from path1 and leading slash from path2
    path1=${path1%/}
    path2=${path2#/}

    # Concatenate paths
    local result_path="$path1/$path2"

    echo "$result_path"
}

create_dir_for_exps_if_not_exists() {
    if [ ! -d "$1" ]; then
        mkdir "${1}"
    fi
}

clone_postgres_repository() {
    local POSTGRES_REPO="https://github.com/postgres/postgres.git"
    local POSTGRES_BRANCH="REL_15_STABLE"
    local POSTGRES_DIR=$1

    if [ ! -d "$POSTGRES_DIR" ]; then
      git clone --branch "$POSTGRES_BRANCH" --depth=1 "$POSTGRES_REPO" "$POSTGRES_DIR"
    else
        echo "PostgresSQL repository already exists in $POSTGRES_DIR"
    fi
}

install_postgres() {
    local POSTGRES_DIR=$1
    local INSTALL_DIR=$2
    cd "$POSTGRES_DIR" || exit

    CONFIGURE_OPTIONS="--prefix=${INSTALL_DIR} --enable-debug --enable-cassert --enable-tap-tests"
    echo "Prefix = ${INSTALL_DIR}"
    echo "Options : ${CONFIGURE_OPTIONS}"
    IFS=' ' read -r -a OPTIONS_ARRAY <<< "$CONFIGURE_OPTIONS"

    config_script="$POSTGRES_DIR/configure"
    "$config_script" "${OPTIONS_ARRAY[@]}"
    make -j12
    make install
}

clone_fs() {
  FS_REPO="https://github.com/dura0ok/pglab-unreliable-fs.git"
  local FS_DIR=$1
  if [ ! -d "$FS_DIR" ]; then
      git clone "$FS_REPO" "$FS_DIR"
    else
        echo "FS repository already exists in $FS_DIR"
  fi
}

init_fs_venv() {
  local FS_DIR=$1
  cd "$FS_DIR" || exit
  python3 -m venv myvenv
  source myvenv/bin/activate
  pip install -r requirements.txt
}

run_fs() {
  local FS_DIR=$1
  local BASE_DIR=$2
  local MNT_DIR_NAME=$3
  cd "$FS_DIR" || exit

  sudo umount "$MNT_DIR_NAME"
  sudo rm -rf "$MNT_DIR_NAME"
  create_dir_for_exps_if_not_exists "$MNT_DIR_NAME"
  python main.py "$MNT_DIR_NAME"  "$BASE_DIR" example-config.json &
}

init_db_dir() {
  local INSTALLED_PG_DIR=$1
  local PG_DATA=$2
  cd "${INSTALLED_PG_DIR}/bin" || exit
  rm -rf "$PG_DATA"
  ./initdb -D "$PG_DATA"
}

start_postgres() {
  local INSTALLED_PG_DIR=$1
  local PG_DATA=$2
  local PORT=${3:-5432}
  "${INSTALLED_PG_DIR}"/bin/pg_ctl -D "$PG_DATA" -l logfile -o "-p $PORT" start
}

create_physical_replica() {
    local PG_BIN_DIR="${1}/bin"
    local REPLICA_DATA_DIR=$2
    "${PG_BIN_DIR}"/createuser --replication replica_user
    rm -rf "$REPLICA_DATA_DIR"
    "${PG_BIN_DIR}"/pg_basebackup -D "${REPLICA_DATA_DIR}" -Fp -Xs -R -c fast -P -h localhost -U replica_user
    sed -i "s/#primary_conninfo = ''/primary_conninfo = 'host=localhost user=replica_user port=5432'/" "${REPLICA_DATA_DIR}/postgresql.conf"
}

create_db_for_tests() {
  local PG_BIN_DIR="${1}/bin"
  "${PG_BIN_DIR}"/createdb "$2"
}

kill_port_process() {
    local port="$1"
    local pid
    pid=$(lsof -t -i :"$port" 2>/dev/null)
    if [ -n "$pid" ]; then
        if kill -9 "$pid" 2>/dev/null; then
            echo "Process running on port $port has been terminated."
        else
            echo "Failed to terminate process running on port $port."
        fi
    else
        echo "No process running on port $port."
    fi
}

main() {
    # Variables
    local TMP_DIR="${TMP_DIR:-/tmp/fuse}"
    local POSTGRES_DIR
    POSTGRES_DIR=$(concat_paths "$TMP_DIR" "postgres")

    local INSTALLED_PG_DIR
    INSTALLED_PG_DIR=$(concat_paths "$TMP_DIR" "pg")

    local FS_DIR
    FS_DIR=$(concat_paths "$TMP_DIR" "pglab")

    local INSTALLED_PG_DATA_DIR
    INSTALLED_PG_DATA_DIR=$(concat_paths "$INSTALLED_PG_DIR" "data")

    local REPLICA_DATA_DIR
    REPLICA_DATA_DIR=$(concat_paths "$INSTALLED_PG_DIR" "replica-data")

    local DB_TESTS_NAME="pg_tests"
    local MNT_DIR
    MNT_DIR=$(concat_paths "$FS_DIR" "fake_postgres")

    echo "POSTGRES_DIR: $POSTGRES_DIR"
    echo "INSTALLED_PG_DIR: $INSTALLED_PG_DIR"
    echo "INSTALLED_PG_DATA_DIR: $INSTALLED_PG_DATA_DIR"
    echo "FSDIR: $FS_DIR"
    echo "MNT_DIR: $MNT_DIR"

    setup_environment > /dev/null
    create_dir_for_exps_if_not_exists "$TMP_DIR"
    clone_postgres_repository "$POSTGRES_DIR"
    install_postgres "$POSTGRES_DIR" "$INSTALLED_PG_DIR"
    clone_fs "$FS_DIR"
    init_fs_venv "$FS_DIR"
    run_fs "$FS_DIR" "$INSTALLED_PG_DIR" "$MNT_DIR"
    init_db_dir "$INSTALLED_PG_DIR" "$INSTALLED_PG_DATA_DIR"
    kill_port_process 5432
    echo "$MNT_DIR"
    # start_postgres "${MNT_DIR}" "${MNT_DIR}/data"
     start_postgres "${INSTALLED_PG_DIR}" "${MNT_DIR}/data"
#    create_db_for_tests "$INSTALLED_PG_DIR" "$DB_TESTS_NAME"
#    create_physical_replica "$INSTALLED_PG_DIR" "$REPLICA_DATA_DIR"
#    start_postgres "$INSTALLED_PG_DIR" "$REPLICA_DATA_DIR" 5433
#    fg
}

main
