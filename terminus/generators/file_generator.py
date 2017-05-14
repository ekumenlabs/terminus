"""
Copyright (C) 2017 Open Source Robotics Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from city_visitor import CityVisitor
from jinja2 import Template, Environment
import textwrap
import re
import os
try:
    from cStringIO import StringIO
except:
    from io import StringIO

jinja_env = Environment(extensions=['jinja2.ext.do'],
                        trim_blocks=True,
                        lstrip_blocks=True)


class FileGenerator(CityVisitor):

    def __init__(self, city):
        super(FileGenerator, self).__init__(city)
        self.template_cache = {}

    def write_to(self, destination_file):
        raw_text = self.generate()
        licence = self.licence(destination_file)
        with open(destination_file, "w") as f:
            if licence:
                f.write(licence)
            f.write(raw_text)

    def generate(self):
        self.document = StringIO()
        self.start_document()
        self.run()
        self.end_document()
        text = self.document.getvalue()
        text = textwrap.dedent(text)
        if text[0] == "\n":
            text = text[1:]
        return text

    def licence(self, destination_file):
        if self.city.get_metadata('builder') and \
           self.city.get_metadata('builder').required_licence():
            filename = os.path.basename(destination_file)
            licence_template = self.city.get_metadata('builder').required_licence()
            licence = licence_template.format(**{'filename': filename})
            return self._prepare_licence(licence)
        return None

    def comment(self, text):
        return text

    # Start/End document handling

    def start_document(self):
        pass

    def end_document(self):
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
            template = jinja_env.from_string(method())
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
        self.document = StringIO()
        self.document.write(new_contents)

    def _wrap_document_with_template(self, key, **kwargs):
        render_params = dict(kwargs)
        render_params['inner_contents'] = self.document.getvalue()
        template = self._get_cached_template(key)
        new_contents = template.render(**render_params)
        self.document = StringIO()
        self.document.write(new_contents)

    def _prepare_licence(self, contents):
        return contents
