# Enable the powerline shell
set powerline_path (python3 -c "import os, powerline; print(os.path.dirname(powerline.__file__))")
set fish_function_path $fish_function_path "$powerline_path/bindings/fish"
powerline-setup
