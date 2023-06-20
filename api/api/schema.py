from rest_framework.schemas.openapi import AutoSchema


class MiddlewareAPISchema(AutoSchema):

    def _get_operation_id(self, path, method):
        operation_id = path.replace("/", "-").strip("-")
        return f"{method.lower()}-{operation_id}"

    def _map_field(self, field):
        if field.field_name == "entities":
            return {
                'type': 'object'
            }
        return super()._map_field(field)

    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        if path.startswith("/sources"):
            operation["tags"] = ["Sources"]
        elif path.startswith("/entities"):
            operation["tags"] = ["Entities"]
        elif path.startswith("/files"):
            operation["tags"] = ["Files"]
        else:
            operation["tags"] = ["default"]
        return operation
