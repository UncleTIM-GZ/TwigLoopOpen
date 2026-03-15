"""Platform quota configuration — default limits."""

# Object volume limits
MAX_WORK_PACKAGES_PER_PROJECT = 5
MAX_TASKS_PER_WORK_PACKAGE = 6
MAX_TASKS_PER_PROJECT = 20
MAX_EWU_PER_TASK = 8

# Founder concurrency limits (new A defaults)
MAX_ACTIVE_PROJECTS_NEW_FOUNDER = 2
MAX_OPEN_SEATS_DEFAULT = 12
MAX_ACTIVE_TASKS_DEFAULT = 30

# Relationship limits
MAX_PENDING_APPLICATIONS_PER_PROJECT = 30
MAX_PENDING_APPLICATIONS_PER_TASK = 10

# Status definitions
ACTIVE_PROJECT_STATUSES = ("draft", "published", "open", "in_progress")
OPEN_SEAT_STATUSES = ("proposed", "on_trial")
ACTIVE_TASK_STATUSES = ("draft", "assigned", "in_progress", "submitted")
PENDING_APPLICATION_STATUSES = ("submitted", "under_review")
