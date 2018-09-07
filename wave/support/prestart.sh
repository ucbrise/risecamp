# this will be sourced
echo "starting daemon"
chmod 755 /support/waved
daemon --name waved --respawn -- /support/waved --config /support/wave.toml
echo "daemon started"
ps -ef
