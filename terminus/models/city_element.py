from jinja2 import Template


# Just an element of the city. It has a template so it can be rendered to an
# sdf file
class CityElement(object):

    def template(self):
        raise NotImplementedError()

    def to_sdf(self):
        template = Template(self.template(),
                            trim_blocks=True,
                            lstrip_blocks=True)
        return template.render(model=self)
