from database import PaniniDatabase


def main():
    db = PaniniDatabase()
    db.connect_database
    db.create_tables()
    db.import_groups_from_csv()
    db.import_teams_from_csv()


if __name__ == "__main__":
    main()