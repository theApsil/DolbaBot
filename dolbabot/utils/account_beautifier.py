def account_beautifier(accounts_data):
    if not accounts_data:
        return []

    max_name_length = max(len(acc.account_name) for acc in accounts_data)

    lines = []

    for account in accounts_data:
        amount_str = f"{abs(account.amount):,.{account.decimals}f}".replace(",", "’")
        name = account.account_name.upper()

        line = f" {name.ljust(max_name_length)}   {amount_str}"
        lines.append(f"`{line}`")

    return lines
