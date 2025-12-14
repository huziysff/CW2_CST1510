class ITTicket:
    def __init__(self, id, ticket_id, subject, priority, status, category, created_date, assigned_to=None):
        self.id = id  # Database Primary Key
        self.ticket_id = ticket_id  # String ID (e.g. TKT-1001)
        self.subject = subject
        self.priority = priority
        self.status = status
        self.category = category
        self.created_date = created_date
        self.assigned_to = assigned_to

    def get_status_emoji(self):
        s = self.status.lower()
        if "open" in s: return "🔴"
        if "waiting" in s: return "Dg"
        if "closed" in s: return "Vk"
        return "⚪"

    def is_assigned(self):
        return self.assigned_to is not None and self.assigned_to != ""