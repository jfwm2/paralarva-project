#!/bin/bash

BASE_DIR=$(dirname "$(readlink -f "$0")")
CONF_TMPL="${BASE_DIR}/tests_docker_config.tmpl"
CONF_YAML="${BASE_DIR}/tests_docker_config.yaml"
BUILD_CHART=$(readlink -f "${BASE_DIR}/../../build_and_deploy_chart.sh")

ES_IMAGE="docker.elastic.co/elasticsearch/elasticsearch:7.11.0"
ES_NETWORK="elastic"

CREATE_CONTAINER=1

PORT=9200
SINGLE_NODE_SERVICE_NAME='es0'
MULTI_NODE_SERVICE_NAME='es1'
MULTI_NODE_SERVICE_SIZE=3

usage() {
  echo "create docker containers and build minikube chart for testing"
  echo "usage: $(basename "$0") [-(d|h|s)]"
  echo "   -d: delete containers"
  echo "   -h: show this message"
  echo "   -s: skip container creation"
}

usage_err() {
  usage >&2
  exit 1
}

get_node_name() {
  CLUSTER_NAME=$1
  NODE_NUMBER=$2
  echo "${CLUSTER_NAME}n${NODE_NUMBER}"
}

delete_container_if_exists() {
  CONTAINER_NAME=$1
  echo "removing container ${CONTAINER_NAME} if it exits"
  CONTAINER_ID=$(docker ps -a -f "name=${CONTAINER_NAME}" --format '{{.ID}}')
  if [[ -z ${CONTAINER_ID} ]]; then
    echo "no container found with name ${CONTAINER_NAME}"
  else
    docker rm --force "${CONTAINER_ID}"
  fi
}

single_node() {
  CONTAINER_NAME=$(get_node_name "$1" 1)
  PORT=$2

  delete_container_if_exists "${CONTAINER_NAME}"
  CONTAINER_ID=$(docker run -d -p "${PORT}":9200 --name "${CONTAINER_NAME}" \
    -e "discovery.type=single-node" ${ES_IMAGE})
  # Not for the current use case
  # CONTAINER_IP=$(docker \
  # 		       inspect -f \
  # 		       '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
  # 		       ${CONTAINER_ID})
  echo "container ${CONTAINER_NAME} created with ID ${CONTAINER_ID}"
}

cluster_node() {
  CLUSTER_NAME=$1
  PORT=$2
  NUMBER_OF_NODES=$3
  NODE_NUMBER=$4
  CONTAINER_NAME=$(get_node_name "${CLUSTER_NAME}" "${NODE_NUMBER}")

  FULL_LIST=''
  PEER_LIST=''
  PEER_COMMA=''
  FULL_COMMA=''
  for n in $(seq "${NUMBER_OF_NODES}"); do
    if [[ ${n} -ne ${NODE_NUMBER} ]]; then
      PEER_LIST="${PEER_LIST}${PEER_COMMA}$(get_node_name "${CLUSTER_NAME}" "${n}")"
      PEER_COMMA=','
    fi
    FULL_LIST="${FULL_LIST}${FULL_COMMA}$(get_node_name "${CLUSTER_NAME}" "${n}")"
    FULL_COMMA=','
  done

  delete_container_if_exists "${CONTAINER_NAME}"
  CONTAINER_ID=$(docker run -d -p "${PORT}":9200 --name "${CONTAINER_NAME}" \
    -e "node.name=${CONTAINER_NAME}" \
    -e "cluster.name=${CLUSTER_NAME}" \
    -e "discovery.seed_hosts=${PEER_LIST}" \
    -e "cluster.initial_master_nodes=${FULL_LIST}" \
    -e "bootstrap.memory_lock=true" \
    -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
    --ulimit memlock=-1:-1 \
    --network ${ES_NETWORK} ${ES_IMAGE})
  echo "container ${CONTAINER_NAME} created with ID ${CONTAINER_ID}"
}

delete_container_cluster() {
  CLUSTER_NAME=$1
  NUMBER_OF_NODES=$2
  for n in $(seq "${NUMBER_OF_NODES}"); do
    delete_container_if_exists "$(get_node_name "${CLUSTER_NAME}" "${n}")"
  done
}

ACTION=''
while getopts 'dhs' OPTION; do
  case "${OPTION}" in
  d) [ -n "${ACTION}" ] && usage_err || ACTION=d ;;
  h) [ -n "${ACTION}" ] && usage_err || ACTION=h ;;
  s) [ -n "${ACTION}" ] && usage_err || ACTION=s ;;
  \?) usage_err ;;
  *) usage_err ;;
  esac
done

case "${ACTION}" in
d)
  delete_container_cluster ${SINGLE_NODE_SERVICE_NAME} 1 &&
    delete_container_cluster ${MULTI_NODE_SERVICE_NAME} \
      ${MULTI_NODE_SERVICE_SIZE}
  exit $?
  ;;
h) usage && exit 0 ;;
s) CREATE_CONTAINER=0 ;;
esac

MINIKUBE_GW=$(minikube ssh "ip route | awk '/^default/ { print \$3 }'")
if [[ -z ${MINIKUBE_GW} ]]; then
  echo "Could not get minikube gateway ip address; exiting"
  exit 2
fi
MINIKUBE_GW="${MINIKUBE_GW%%[[:cntrl:]]}" # stripping extra CR

cat <<EOF >"${CONF_YAML}"
# !!! this file was generated by $(basename "$0") !!!
# !! do not modify manually as changes may be overridden !!

EOF
cat "${CONF_TMPL}" >>"${CONF_YAML}"

((CREATE_CONTAINER)) && single_node ${SINGLE_NODE_SERVICE_NAME} "${PORT}"

cat <<EOF >>"${CONF_YAML}"
    - name: ${SINGLE_NODE_SERVICE_NAME}
      domain: ${SINGLE_NODE_SERVICE_NAME}
      hosts:
        - address: "${MINIKUBE_GW}"
          port: ${PORT}
    - name: ${MULTI_NODE_SERVICE_NAME}
      domain: ${MULTI_NODE_SERVICE_NAME}
      hosts:
EOF

((CREATE_CONTAINER)) && docker network create ${ES_NETWORK}

for n in $(seq ${MULTI_NODE_SERVICE_SIZE}); do
  ((++PORT))
  ((CREATE_CONTAINER)) && cluster_node ${MULTI_NODE_SERVICE_NAME} "${PORT}" ${MULTI_NODE_SERVICE_SIZE} "${n}"
  cat <<EOF >>"${CONF_YAML}"
        - address: "${MINIKUBE_GW}"
          port: ${PORT}
EOF
done

echo '' >>"${CONF_YAML}"

# first three "warning" lines are excluded to build the chart
${BUILD_CHART} <(sed -e '1,3d' "${CONF_YAML}")
