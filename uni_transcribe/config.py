

class Config:
    def __init__(self, language=None, google_storage_bucket=None, s3_bucket=None):
        self.language = language
        self.google_storage_bucket = google_storage_bucket
        self.s3_bucket = s3_bucket
