c = get_config()

c.InteractiveShellApp.extensions = [
    'powerline.bindings.ipython.post_0_11'
]
c.TerminalInteractiveShell.confirm_exit = False
