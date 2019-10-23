from tkinter import *
from PIL import ImageTk, Image
from threading import Lock, Thread
from time import sleep
from random import randrange


root = Tk()


class Philosopher(object):
    STATE_AVATARS = {
        'eating': ImageTk.PhotoImage(Image.open("eating.jpg")),
        'thinking': ImageTk.PhotoImage(Image.open("thinking.jpg")),
        'out': ImageTk.PhotoImage(Image.open("chair.jpg").resize((128, 128)))
    }

    def __init__(self, name, philosopher_id):
        self.philosopher_id = philosopher_id
        self.name = name
        self.avatar = ImageTk.PhotoImage(Image.open("{}.jpg".format(self.name.lower())))
        self.panel = Label(root, image=self.avatar)
        self.acquired = False
        self.left_fork = None
        self.right_fork = None

    def acquire(self):
        self.panel.configure(image=self.avatar)
        self.panel.image = self.avatar
        if not self.acquired:
            self.left_fork.mutex.acquire()
            self.right_fork.mutex.acquire()
            self.left_fork.panel.configure(image=self.left_fork.AVATARS['used'])
            self.left_fork.panel.image = self.left_fork.AVATARS['used']
            self.right_fork.panel.configure(image=self.right_fork.AVATARS['used'])
            self.right_fork.panel.image = self.right_fork.AVATARS['used']
            self.acquired = True

    def release(self):
        self.panel.configure(image=self.avatar)
        self.panel.image = self.avatar
        if self.acquired:
            self.left_fork.mutex.release()
            self.right_fork.mutex.release()
            self.left_fork.panel.configure(image=self.left_fork.AVATARS['available'])
            self.left_fork.panel.image = self.left_fork.AVATARS['available']
            self.right_fork.panel.configure(image=self.right_fork.AVATARS['available'])
            self.right_fork.panel.image = self.right_fork.AVATARS['available']
            self.acquired = False
        else:
            print("{} couldn't release the forks since it didn't have them.\n".format(self.name))

    def eat(self):
        if self.left_fork.mutex.locked() and self.right_fork.mutex.locked():
            self.panel.configure(image=self.STATE_AVATARS['eating'])
            self.panel.image = self.STATE_AVATARS['eating']
            print("{} is eating... Yummy!\n".format(self.name))
            random_eating = randrange(10) + 1
            sleep(random_eating)
        else:
            print("{} couldn't eat.".format(self.name))

    def think(self):
        self.panel.configure(image=self.STATE_AVATARS['thinking'])
        self.panel.image = self.STATE_AVATARS['thinking']
        print("{} is thinking...\n".format(self.name))
        random_sleep = randrange(10) + 1
        sleep(random_sleep)

    def set_left_fork(self, left_obj):
        self.left_fork = left_obj

    def set_right_fork(self, right_obj):
        self.right_fork = right_obj


class Fork(object):
    AVATARS = {
        'available': ImageTk.PhotoImage(Image.open("fork.jpg").resize((64, 64))),
        'used': ImageTk.PhotoImage(Image.open("blue_fork.jpg").resize((64, 64)))
    }

    def __init__(self, fork_id):
        self.fork_id = fork_id
        self.avatar = self.AVATARS['available']
        self.panel = Label(root, image=self.avatar)
        self.mutex = Lock()

    def __str__(self):
        return str(self.fork_id)


class Table(object):
    MAX_NUMBER_PHILOSOPHERS = 5
    PHILOSOPHER_NAMES = ["Socrates", "Plato", "Descartes", "Nietzsche", "Kant"]

    def __init__(self):
        self.philosophers = list()
        self.forks = list()
        self.philosophers = [Philosopher(name, count) for count, name in enumerate(self.PHILOSOPHER_NAMES)]
        self.threads = list()
        for j in range(0, self.MAX_NUMBER_PHILOSOPHERS):
            current_fork = Fork(j)
            self.forks.append(Fork(j))
            if j == (self.MAX_NUMBER_PHILOSOPHERS - 1):
                current_fork.panel.pack(side="left", fill="both", expand="yes")
                self.philosophers[j].panel.pack(side="left", fill="both", expand="yes")
                self.philosophers[0].set_left_fork(current_fork)
            else:
                current_fork.panel.pack(side="left", fill="both", expand="yes")
                self.philosophers[j].panel.pack(side="left", fill="both", expand="yes")
                self.philosophers[j+1].set_left_fork(current_fork)
            self.philosophers[j].set_right_fork(current_fork)

    def run(self):
        self.threads = [Thread(target=self.eat_dinner, args=(philosopher, ))for philosopher in self.philosophers]
        for thread in self.threads:
            thread.start()

    def join(self):
        for thread in self.threads:
            thread.join()

    @staticmethod
    def eat_dinner(philosopher_ins):
        list_func = [philosopher_ins.eat, philosopher_ins.acquire, philosopher_ins.release, philosopher_ins.think]
        for i in range(10):
            function = list_func[randrange(4)]
            print("{}.- {} decided to {}.\n".format(i+1, philosopher_ins.name, function.__name__))
            function()
        philosopher_ins.release()
        philosopher_ins.panel.configure(image=philosopher_ins.STATE_AVATARS['out'])
        philosopher_ins.panel.image = philosopher_ins.STATE_AVATARS['out']
        print("{} is leaving. Bye, bye!\n".format(philosopher_ins.name))


if __name__ == '__main__':
    table = Table()
    table.run()
    root.mainloop()
    table.join()
