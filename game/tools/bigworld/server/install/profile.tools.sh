if [ -n "$BASH_VERSION" -o -n "$KSH_VERSION" -o -n "$ZSH_VERSION" ]; then
  PATH=${PATH}:/opt/bigworld/current/tools
  PATH=${PATH}:/opt/bigworld/current/tools/message_logger
  PATH=${PATH}:/opt/bigworld/current/tools/space_viewer
  export PATH

  MANPATH=${MANPATH}:/opt/bigworld/current/tools/man
  export MANPATH
fi
