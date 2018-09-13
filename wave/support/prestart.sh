# this will be sourced
chmod 755 /usr/local/bin/waved
daemon --name waved --respawn -- /usr/local/bin/waved --config /usr/local/bin/wave.toml
