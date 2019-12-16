import sys

from app import Application

sys.setrecursionlimit(pow(2, 16))
sys.exit(Application(sys.argv).run())
