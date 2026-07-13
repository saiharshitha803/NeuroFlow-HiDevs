from contextlib import nullcontext


class DummySpan:
    def __init__(self):
        self.attributes = {}

    def set_attribute(self, key, value):
        self.attributes[key] = value


class IngestionTelemetry:
    def start_span(self):
        return nullcontext(DummySpan())

    def add_attributes(self, span, **kwargs):
        for key, value in kwargs.items():
            span.set_attribute(key, value)