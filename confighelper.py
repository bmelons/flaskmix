import json

class MapObject:
    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, MapObject(value))
            else:
                setattr(self, key, value)