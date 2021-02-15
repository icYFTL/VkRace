from sys import platform

class ProgressBar:
    def __init__(self, start=0, end=100, gates=('[', ']'), title='ProgressBar', length=50):
        self.start = start
        self.end = end
        self.gates = gates
        self.title = title
        self.length = length

    @staticmethod
    def to_fixed(num_obj, digits=2):
        return f"{num_obj:.{digits}f}"

    def update(self, value):
        template = '{title}: {start_gate}{body}{end_gate} {percent}%'

        percent = float(value) * 100 / self.end
        arrow = '-' * int(percent / 100 * self.length - 1) + '>'
        spaces = ' ' * (self.length - len(arrow))

        print(template.format(
            title=self.title,
            start_gate=self.gates[0],
            body=arrow + spaces,
            end_gate=self.gates[1],
            percent=ProgressBar.to_fixed(percent)
        ), end='\r')

    def stop(self):
        print('\r\n')
