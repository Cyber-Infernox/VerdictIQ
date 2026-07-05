from data_collector import get_recent_form, get_head_to_head

print("=== INTERNATIONAL ===")
print("Argentina:", get_recent_form("Argentina"))
print("Brazil:", get_recent_form("Brazil"))
print("France:", get_recent_form("France"))
print()

print("=== CLUB ===")
print("Real Madrid:", get_recent_form("Real Madrid"))
print("Barcelona:", get_recent_form("Barcelona"))
print("Manchester United:", get_recent_form("Manchester United"))
print("Liverpool:", get_recent_form("Liverpool"))
print()

print("=== HEAD TO HEAD ===")
print("Argentina vs Brazil:", get_head_to_head("Argentina", "Brazil"))
print("Real Madrid vs Barcelona:", get_head_to_head("Real Madrid", "Barcelona"))
print("Man Utd vs Liverpool:", get_head_to_head("Manchester United", "Liverpool"))