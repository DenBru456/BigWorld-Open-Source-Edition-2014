if [ -n "$BASH_VERSION" -o -n "$KSH_VERSION" -o -n "$ZSH_VERSION" ]; then
  PATH=${PATH}:/opt/bigworld/current/server/bin
  PATH=${PATH}:/opt/bigworld/current/server/bigworld/bin/Hybrid64
  PATH=${PATH}:/opt/bigworld/current/server/bigworld/bin/Hybrid64/commands
  export PATH
fi
