from database import PaniniDatabase


def main():
    db = PaniniDatabase()
    db.connect_database
    db.create_tables()
    db.import_groups_from_csv()
    db.import_teams_from_csv()
    db.import_stickers_from_csv()
    db.create_collection_rows()

    """code = input("Enter sticker code: ")
    sticker = db.get_sticker_by_code(code)

    if sticker:
        print("Sticker found:")
        print("Code:", sticker["sticker_code"])
        print("Name:", sticker["player_name"])
        print("Team:", sticker["team_name"])
        print("Quantity:", sticker["quantity"])
    else:
        print("Sticker not found.") """

    """ code = input("Enter sticker code to add: ")
    sticker = db.add_sticker(code)

    if sticker:
        print("Sticker added successfully.")
        print("Code:", sticker["sticker_code"])
        print("Name:", sticker["player_name"])
        print("Team:", sticker["team_name"])
        print("New quantity:", sticker["quantity"])
    else:
        print("Sticker not found.") """

    #db.get_owned_stickers()

    team = input("Enter team: ")
    team_selected = db.get_team_progress(team)

    if team_selected:
        first_row = team_selected[0]

        print("Team:", first_row["team_name"])
        print("FIFA Code:", first_row["fifa_code"])
        print("Group:", first_row["group_name"])

        owned_stickers = []
        missing_stickers = []

        for row in team_selected:
            if row["quantity"] >= 1:
                owned_stickers.append(row)
            else:
                missing_stickers.append(row)

        print("Owned Stickers:")
        for row in owned_stickers:
            print(
                f"Sticker Code: {row['sticker_code']} | "
                f"Player Name: {row['player_name']} | "
                f"Quantity: {row['quantity']}"
            )

        print("\nMissing Stickers:")
        for row in missing_stickers:
            print(
                f"Sticker Code: {row['sticker_code']} | "
                f"Player Name: {row['player_name']} | "
                f"Quantity: {row['quantity']}"
            )
                    
    else:
        print("Team not found.")




if __name__ == "__main__":
    main()