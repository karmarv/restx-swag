class JobException(Exception):
    def __init__(self, message='Job error', error_field_name='unknown_field', *args, **kwargs):
        super().__init__(args, **kwargs)
        self.error_field_name = error_field_name
        self.message = message