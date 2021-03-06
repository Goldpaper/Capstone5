class Getch(object):
    def __init__(self):
        try:
            self.impl = self.init_windows()
        except ImportError:
            self.impl = self.init_unix()

    def __call__(self):
        return self.impl()

    def init_windows(self):
        import msvcrt
        return msvcrt.getch

    def init_unix(self):
        import sys, tty, termios

        def _func():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

        return _func
