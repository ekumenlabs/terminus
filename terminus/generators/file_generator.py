from jinja2 import Template
import textwrap
import re
try:
    from cStringIO import StringIO
except:
    from io import StringIO


class FileGenerator(object):

    def __init__(self, city):
        self.city = city
        self.template_cache = {}

    def write_to(self, destination_file):
        raw_text = self.generate()
        raw_text = textwrap.dedent(raw_text)
        if raw_text[0] == "\n":
            raw_text = raw_text[1:]
        with open(destination_file, "w") as f:
            f.write(raw_text)

    def generate(self):
        self.document = StringIO()
        self.start_document()
        self.city.accept(self)
        self.end_document()
        return self.document.getvalue()

    # Start/End document handling

    def start_document(self):
        pass

    def end_document(self):
        pass

    # Double-dispatching methods. By default do nothing. Override in subclasses
    # to build the required file contents

    def start_city(self, city):
        pass

    def end_city(self, city):
        pass

    def start_street(self, city):
        pass

    def end_street(self, city):
        pass

    def start_trunk(self, city):
        pass

    def end_trunk(self, city):
        pass

    def start_ground_plane(self, city):
        pass

    def end_ground_plane(self, city):
        pass

    def start_block(self, city):
        pass

    def end_block(self, city):
        pass

    def start_building(self, city):
        pass

    def end_building(self, city):
        pass

    # Private, template management

    def _contents_for(self, model, **kwargs):
        render_params = dict(kwargs)
        render_params['model'] = model
        render_params['generator'] = self
        template = self._cached_template_for(model)
        return template.render(**render_params)

    def _cached_template_for(self, object):
        key = self._template_cache_key_for(object)
        return self._get_cached_template(key)

    def _get_cached_template(self, key):
        if key not in self.template_cache:
            method_name = key + '_template'
            method = getattr(self, method_name)
            template = Template(method(),
                                trim_blocks=True,
                                lstrip_blocks=True)
            self.template_cache[key] = template
        return self.template_cache[key]

    # See http://stackoverflow.com/questions/1175208/
    # elegant-python-function-to-convert-camelcase-to-snake-case
    def _template_cache_key_for(self, model):
        class_name = model.__class__.__name__
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    # Private, stream management
    def _append_to_document(self, contents):
        self.document.write(contents)

    def _wrap_document_with_contents_for(self, model, **kwargs):
        params = dict(kwargs)
        params['inner_contents'] = self.document.getvalue()
        new_contents = self._contents_for(model, **params)
        self.document = StringIO(new_contents)

    def _wrap_document_with_template(self, key, **kwargs):
        render_params = dict(kwargs)
        render_params['inner_contents'] = self.document.getvalue()
        template = self._get_cached_template(key)
        new_contents = template.render(**render_params)
        self.document = StringIO(new_contents)
