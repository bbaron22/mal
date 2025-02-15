import os
import readline as pyreadline

history_loaded = False
histfile = os.path.expanduser("~/.mal-history")
rl = input


def readline(prompt="user> "):
    global history_loaded
    line = ''
    if not history_loaded:
        history_loaded = True
        try:
            with open(histfile, "r") as hf:
                for line in hf.readlines():
                    pyreadline.add_history(line.rstrip("\r\n"))
                    pass
        except IOError:
            # print("Could not open %s" % histfile)
            pass

    try:
        line = rl(prompt)
        pyreadline.add_history(line)
        with open(histfile, "a") as hf:
            hf.write(line + "\n")
    except IOError:
        pass
    except EOFError:
        return None
    return line
