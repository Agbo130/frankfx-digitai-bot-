def update_session(account_id, balance):
    try:
        with open("session.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    data["account_id"] = account_id
    data["balance"] = "{:.2f}".format(balance)
    with open("session.json", "w") as f:
        json.dump(data, f)
