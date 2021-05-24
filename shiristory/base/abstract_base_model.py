from datetime import datetime

from django.db.models import ManyToManyField, DateTimeField
from djongo import models
from djongo.models import ArrayField

from shiristory.settings import DATETIME_FORMAT


class AbstractBaseModel(models.Model):

    def to_dict(self, fields=None, exclude=None):
        data = {}
        for f in self._meta.concrete_fields + self._meta.many_to_many:
            value = f.value_from_object(self)

            if fields and f.name not in fields:
                continue

            if exclude and f.name in exclude:
                continue

            # Convert mongodb id to string
            if f.name == '_id':
                value = str(value)

            if isinstance(f, ManyToManyField):
                value = [str(i.id) for i in value] if self.pk else None

            # TODO
            # if isinstance(f, EmbeddedField):
            #     value = value.to_dict()

            if isinstance(f, DateTimeField):
                value = value.strftime(DATETIME_FORMAT) if value else None

            # Convert ArrayField datetime field into DATETIME_FORMAT
            if isinstance(f, ArrayField):
                if len(value) != 0:
                    temp = []
                    first_item = value[0]

                    if type(first_item) is dict:
                        date_keys = []
                        # Get fields of datetime
                        for key, item_value in first_item.items():
                            if isinstance(item_value, datetime):
                                date_keys.append(key)
                        # Format datetime and add to temp
                        for item in value:
                            for date_key in date_keys:
                                item[date_key] = item[date_key].strftime(DATETIME_FORMAT)
                            temp.append(item)
                    # If value is array of datetime
                    elif isinstance(first_item, datetime):
                        for item in value:
                            temp.append(item.strftime(DATETIME_FORMAT))

                    value = temp

            data[f.name] = value

        return data

    class Meta:
        abstract = True
