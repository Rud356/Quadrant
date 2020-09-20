from datetime import datetime

from quart.json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()

            iterable = map(self.default, obj)
        except TypeError:
            pass

        else:
            return list(iterable)

        return JSONEncoder.default(self, obj)
