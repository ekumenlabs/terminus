from jinja2 import Template


# Just an element of the city. It has a template so it can be rendered to an
# sdf file
class CityElement(object):

    @classmethod
    def template(cls):
        raise NotImplementedError()

    @classmethod
    def cached_jinja_template(cls):
        if not hasattr(cls, '_cached_jinja_template'):
            cls._cached_jinja_template = Template(cls.template(),
                                                  trim_blocks=True,
                                                  lstrip_blocks=True)
        return cls._cached_jinja_template

    def jinja_template(self):
        return self.cached_jinja_template()

    def to_sdf(self):
        return self.jinja_template().render(model=self)
