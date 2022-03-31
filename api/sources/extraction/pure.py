class PureAPIMixin(object):

    @classmethod
    def get_api_count(cls, data):
        return data["count"]

    @classmethod
    def get_api_next_cursor(cls, data):
        info = data["pageInformation"]
        next_offset = info['offset'] + info['size']
        if next_offset > cls.get_api_count(data):
            print(next_offset, info['size'])
            return
        return f"offset|{next_offset}|{info['size']}"

    @classmethod
    def get_api_previous_cursor(cls, data):
        info = data["pageInformation"]
        previous_offset = info['offset'] - info['size']
        if previous_offset < 0:
            return
        return f"offset|{previous_offset}|{info['size']}"

    @classmethod
    def get_api_results_path(cls):
        return "$.items"
