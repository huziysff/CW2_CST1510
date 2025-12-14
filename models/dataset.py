class Dataset:
    def __init__(self, id, name, file_path, row_count, created_date, description=None):
        self.id = id
        self.name = name
        self.file_path = file_path
        self.row_count = row_count
        self.created_date = created_date
        self.description = description

    def get_summary(self):
        """Returns a quick summary string for the UI."""
        return f"📂 {self.name} ({self.row_count} rows) - Uploaded: {self.created_date}"

    def is_large_file(self):
        """Returns True if the dataset has more than 10,000 rows."""
        return self.row_count > 10000

    def __str__(self):
        return f"Dataset(id={self.id}, name='{self.name}')"