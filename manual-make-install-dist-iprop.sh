cversion=$(cat pyproject.toml |tr '"' " " |awk '/version/ {print $3}')
make dist  && \
	pip uninstall jgtfxcon -y && \
  	pip install --user dist/jgtfxcon-$cversion-py3-none-any.whl  && \
  	jgtfxcli --iprop && echo "--------TST1 passed "

