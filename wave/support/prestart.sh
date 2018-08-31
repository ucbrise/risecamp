# this will be sourced
echo "starting daemon"
daemon --name waved --respawn -- /support/waved --config /support/wave.toml
echo "daemon started"
ps -ef
