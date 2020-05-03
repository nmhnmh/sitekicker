import jinja2

class EntryTemplate():
    def __init__(self, path, template):
        self.path = path
        self.template = template

    def __str__(self):
        return "Entry Template At: [%s]" % self.path

    def render(self, data):
        return self.template.render(data)
