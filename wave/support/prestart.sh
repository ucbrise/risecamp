# this will be sourced
echo "starting daemon"
chmod 755 /usr/local/bin/waved
daemon --name waved --respawn -- /usr/local/bin/waved --config /usr/local/bin/wave.toml
echo "daemon started"
ps -ef
