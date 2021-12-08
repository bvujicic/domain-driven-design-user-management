import dataclasses


class ValueObjectUpdateMixin:
    def create_with_changed_atrributes(self, **kwargs):
        return dataclasses.replace(
            self, **{field.name: kwargs.get(field.name) for field in dataclasses.fields(self) if field.name in kwargs}
        )
