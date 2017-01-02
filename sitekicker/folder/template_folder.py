class TemplateFolder:
    def __init__(self, site, path):
        self.path = path
        self.site = site

    def __str__(self):
        return "TemplateFolder: [%s]" % self.path