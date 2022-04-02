class PureAPIMixin(object):

    response = None

    @classmethod
    def get_api_count(cls, data):
        return data["count"]

    def get_api_next_cursor_link(self, data):
        info = data["pageInformation"]
        next_offset = info['offset'] + info['size']
        if next_offset > self.get_api_count(data):
            return
        base_url = self.response.url[:self.response.url.find("?")]
        return f"{base_url}?cursor=offset|{next_offset}|{info['size']}"

    def get_api_previous_cursor_link(self, data):
        info = data["pageInformation"]
        previous_offset = info['offset'] - info['size']
        if previous_offset < 0:
            return
        base_url = self.response.url[:self.response.url.find("?")]
        return f"{base_url}?cursor=offset|{previous_offset}|{info['size']}"

    @classmethod
    def get_api_results_path(cls):
        return "$.items"
