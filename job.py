from threading import Thread
import subprocess


def start_subprocess(*argv):
    def temp():
        subprocess.run(["./venv/Scripts/python", "main.py",
                        str(argv[0]), str(argv[1]), str(argv[2])
                        ]
                       )

    t = Thread(target=temp)
    t.start()


if __name__ == '__main__':
    start_subprocess(1, 200, 10)
    start_subprocess(201, 300, 10)
