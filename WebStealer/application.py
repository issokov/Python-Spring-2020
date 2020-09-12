import json
from WebStealer import WebStealer
from multiprocessing import Process, Value
from pprint import pprint
from time import sleep
from datetime import datetime, timedelta
from matplotlib.pyplot import plot, show


class App:

    stealer = WebStealer(urls_json_fname="url_list.json")
    update_delay = 30

    def __init__(self):
        self.is_run = Value('b', False)
        self.stealer_proc = Process(target=self.run_stealer, args=tuple([self.is_run]))

    def run(self):
        self.is_run.value = True
        self.stealer_proc.start()
        self.run_cmd()
        self.stealer_proc.join()

    def run_stealer(self, is_run: Value):
        while is_run.value:
            self.stealer.update()
            print(f'Updated at {datetime.now()}')
            sleep(self.update_delay)
        print("ENDED")

    def take_from_last_hours(self, stamps, n, m):
        left_bound = (datetime.now() - timedelta(hours=n)).timestamp()
        right_bound = (datetime.now() - timedelta(hours=m)).timestamp()
        lindex, rindex = None, len(stamps)
        for index, stamp in enumerate(stamps):
            if stamp[0] >= left_bound and lindex is None:
                lindex = index
            if stamp[0] > right_bound and rindex == len(stamps):
                rindex = index
                break
        return stamps[lindex:rindex]

    def get_stats(self, url, data, n=1, m=0):
        stamps = data['updates']
        hour_stamps = self.take_from_last_hours(stamps, n, m)
        updates = 0
        for index in range(len(hour_stamps)-1):
            if hour_stamps[index][1] != hour_stamps[index + 1][1]:
                updates += 1
        return (url, updates)

    def uph_show(self, command, updates):
        fr, to = 1, 0
        command = command.split()
        if len(command) == 3 and command[0] == 'uph':
            try:
                fr, to = map(int, command[1:])
            except ValueError:
                print('Wrong args, try: uph 10 9\n It show stats in period 9..10 hours ago')
        stats = [self.get_stats(url, data, fr, to) for url, data in updates.items()]
        stats.sort(key=lambda x: x[1], reverse=True)
        for url, updates in stats:
            print(f'{updates} updates on {url} website')

    def plot_show(self, updates):
        min_ = min(item['updates'][0][0] for item in updates.values())
        first_record = int((datetime.now()-datetime.fromtimestamp(min_)).total_seconds()/3600)
        x, y = list(range(first_record, -1, -1)), []
        for hour in range(first_record, -1, -1):
            y.append(sum(self.get_stats(url, updates[url], hour + 1, hour)[1] for url in updates.keys()))
        print(x)
        print(y)
        plot(x, y)
        show()

    def run_cmd(self):
        while True:
            command = input().lower()
            if command == 'exit':
                self.is_run.value = False
                print("Please, wait, we turn off the process...")
                break
            else:
                with open('stamps.json', 'r', encoding='utf-8') as file:
                    updates = json.loads(file.read())
                    if command == 'full':
                        pprint(updates)
                    elif command == 'stealer off':
                        self.is_run.value = False
                        print("Please, wait, we turn off the process...")
                    elif command == 'stealer on':
                        self.is_run.value = True
                        print("Please, wait, we turn on the process...")
                    elif 'uph' in command:
                        self.uph_show(command, updates)
                    elif command == 'plot':
                        self.plot_show(updates)


if __name__ == "__main__":
    App().run()
