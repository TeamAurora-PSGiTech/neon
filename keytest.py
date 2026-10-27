import sys, termios, tty
fd = sys.stdin.fileno()
old = termios.tcgetattr(fd)
tty.setraw(fd)
print("Tap a key once. It should print instantly.")
sys.stdout.flush()
print("KEY =", sys.stdin.read(1))
termios.tcsetattr(fd, termios.TCSADRAIN, old)
