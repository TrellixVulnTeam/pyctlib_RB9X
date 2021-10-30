from matplotlib import pyplot as plt
from ..vector import vector
from ..table import table

class animation_content:

    def __init__(self, ax, max_frame):
        self.ax = ax
        self.max_frame = max_frame
        self.default_colors = [u'b', u'g', u'r', u'c', u'm', u'y', u'k']
        self.title_func = None

    def set_titlefunc(self, title_func):
        self.title_func = title_func

    def set_xlim(self, x_low, x_max):
        self.ax.set_xlim(x_low, x_max)

    def set_ylim(self, y_low, y_max):
        self.ax.set_ylim(y_low, y_max)

    def set_xticks(self, *args, **kwargs):
        self.ax.xticks(*args, **kwargs)

    def set_yticks(self, *args, **kwargs):
        self.ax.yticks(*args, **kwargs)

    def init(self):
        ret = tuple()
        if self.title_func:
            self.title = ax.set_title(self.title_func(0))
            ret = ret + tuple([self.title])
        return ret

    def update(self):
        ret = tuple()
        if self.title_func:
            self.title.set_text(self.title_func(frame))
            ret = ret + tuple([self.title])
        return ret

class ScatterAnimation(animation_content):

    def __init__(self, ax, max_frame):
        super().__init__(ax, max_frame)
        self.scatter_dots = vector()

    def register(self, content, **kwargs):
        """
        content.shape: [T, N, 2]
        """
        dots = table(content=content, color=self.default_colors[len(self.dots)], label=None)
        dots.update_exist(kwargs)
        self.scatter_dots.append(dots)

    def init(self):
        self.lines = vector()
        for dots in self.scatter_dots:
            ln, = self.ax.plot([], [], 'o', color=dots["color"], label=dots["label"])
            self.lines.append(ln)
        self.ax.legend()
        return tuple(self.lines) + super().init()

    def update(self, frame):
        for line, dots in vector.zip(self.lines, self.scatter_dots):
            line.set_data(dots["content"][frame, :, 0], dots["content"][frame, :, 1])
        return tuple(self.lines) + super().update(frame)

class TimeStamp(animation_content):

    def __init__(self, ax, max_frame):
        super().__init__(ax, max_frame)
        self.curves = vector()

    def register(self, content, **kwargs):
        assert isinstance(content, list)
        content = vector(content)
        assert content.length >= self.max_frame
        content = content[:self.max_frame]
        curve = table(content=content, color=self.default_colors[len(self.curves)], linewidth=1, label=None)
        curve.update_exist(kwargs)
        self.curves.append(curve)

    def init(self):
        self.N = len(self.curves)
        lines = vector()
        for index, curve in enumerate(self.curves):
            ln, = self.ax.plot(range(self.max_frame), curve["content"], color=curve["color"], linewidth=curve["linewidth"], label=None)
            lines.append(ln)
        self.ax.legend()
        self.dots = self.ax.scatter(vector.zeros(self.N), self.curves.map(lambda x: x["content"][0]), color=self.curves.map(lambda x: x["color"]))
        return tuple(lines.append(self.dots)) + super().init()

    def update(self, frame):
        self.dots.set_offsets(vector.zip(vector.constant_vector(frame, self.N), self.curves.map(lambda x: x["content"][frame])))
        return tuple([self.dots]) + super().update(frame)
