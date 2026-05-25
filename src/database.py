import sqlite3, csv
from pathlib import Path

class PaniniDatabase:
    """A simple in-memory database for storing key-value pairs."""
    def __init__(self):
        self.data = {}
        self.csv_path = Path(__file__).resolve().parent.parent / "data" / "stickers.csv"

    def insert(self, key, value):
        self.data[key] = value

    def retrieve(self, key):
        return self.data.get(key, None)

    def delete(self, key):
        if key in self.data:
            del self.data[key]

    def connect_database(self):
        db_path = Path(__file__).resolve().parent.parent / "data" / "panini.db" #find database path

        conn  = sqlite3.connect(db_path) # connect to database 
        conn.row_factory = sqlite3.Row # make columns accessible by name

        conn.execute("PRAGMA foreign_keys = ON") # make table relationships work properly

        return conn # return connection to db so it can be used by other functions

    def create_tables(self):
        conn = self.connect_database() # connect to database
        cursor = conn.cursor() # create a cursor
        
        # sql statements to create tables
        sql_create = [
                 """CREATE TABLE IF NOT EXISTS 
                groups(
                group_id integer primary key,
                group_name TEXT UNIQUE NOT NULL
            );
            """,
            """CREATE TABLE IF NOT EXISTS 
            teams(
                team_id INTEGER PRIMARY KEY,
                team_name TEXT UNIQUE NOT NULL,
                fifa_code TEXT,
                group_id INTEGER,
                FOREIGN KEY (group_id) REFERENCES groups (group_id)
            );
            """,
            """CREATE TABLE IF NOT EXISTS 
            stickers(
                sticker_id INTEGER PRIMARY KEY,
                sticker_code TEXT UNIQUE NOT NULL,
                sticker_number INTEGER,
                player_name TEXT,
                position TEXT,
                club TEXT,
                page_number INTEGER,
                sticker_type TEXT,
                is_foil INTEGER,
                team_id INTEGER,
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            );
            ""","""CREATE TABLE IF NOT EXISTS 
            collection(
                quantity INTEGER NOT NULL,
                date_added DATE,
                date_updated DATE,
                notes TEXT,
                sticker_id INTEGER PRIMARY KEY,
                FOREIGN KEY (sticker_id) REFERENCES stickers (sticker_id)
            );
            """,
        ]
        
        for statement in sql_create: # execute each statement
            cursor.execute(statement)
        
        conn.commit() # commit changes 
        conn.close() # close connection
    
    # csv file including sticker data

    def import_groups_from_csv(self):
        #read csv
        with open(self.csv_path, newline="", encoding="utf-8-sig") as csvfile: 
            content = csv.DictReader(csvfile)

            unique_groups = set()

            for row in content:
                group_name = row["group_name"].strip()
                if group_name:
                    unique_groups.add(group_name)

            #print(sorted(unique_groups))
            conn = self.connect_database() # connect to database
            cursor = conn.cursor() # create a cursor

            for group_name in sorted(unique_groups):
                cursor.execute(
                    "INSERT OR IGNORE INTO groups (group_name) VALUES (?)",
                    (group_name,)
                )
            conn.commit()
            conn.close()

    def import_teams_from_csv(self):
        unique_teams = set()

        # Read CSV and collect unique teams
        with open(self.csv_path, newline="", encoding="utf-8-sig") as csvfile:
            content = csv.DictReader(csvfile)

            for row in content:
                team = row["team"].strip()
                fifa_code = row["prefix"].strip()
                group_name = row["group_name"].strip()

                if team:
                    unique_teams.add((team, fifa_code, group_name))

        #print(sorted(unique_teams))

        conn = self.connect_database()
        cursor = conn.cursor()

        for team, fifa_code, group_name in sorted(unique_teams):
            cursor.execute(
                "SELECT group_id FROM groups WHERE group_name = ?",
                (group_name,)
            )

            group = cursor.fetchone()

            if group:
                group_id = group["group_id"]
            else:
                group_id = None

            cursor.execute(
                """
                INSERT OR IGNORE INTO teams (team_name, fifa_code, group_id)
                VALUES (?, ?, ?)
                """,
                (team, fifa_code, group_id)
            )

        conn.commit()
        conn.close()

    def import_stickers_from_csv(self):
        conn = self.connect_database()
        cursor = conn.cursor()

        with open(self.csv_path, newline="", encoding="utf-8-sig") as csvfile:
            content = csv.DictReader(csvfile)

            for row in content:
                sticker_code = row["sticker_code"].strip()
                sticker_number = row["item_number"].strip()
                sticker_type = row["sticker_type"].strip()
                is_foil = row["is_foil"].strip().lower()
                team_name = row["team"].strip()
                player_name = row["player_name"].strip()
                item_name = row["item_name"].strip()
                club = row["player_club"].strip()
                page_number = row["page_number"].strip()

                if not sticker_code:
                    continue

                # Convert blank values
                sticker_number = int(sticker_number) if sticker_number.isdigit() else None
                page_number = int(page_number) if page_number.isdigit() else None

                # Convert foil value to 0 or 1
                is_foil = 1 if is_foil in ["true", "yes", "1", "y"] else 0

                # If player_name is blank, use item_name instead
                display_name = player_name if player_name else item_name

                # Find team_id
                team_id = None

                if team_name:
                    cursor.execute(
                        "SELECT team_id FROM teams WHERE team_name = ?",
                        (team_name,)
                    )

                    team = cursor.fetchone()

                    if team:
                        team_id = team["team_id"]

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO stickers (
                        sticker_code,
                        sticker_number,
                        player_name,
                        position,
                        club,
                        page_number,
                        sticker_type,
                        is_foil,
                        team_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sticker_code,
                        sticker_number,
                        display_name,
                        None,
                        club,
                        page_number,
                        sticker_type,
                        is_foil,
                        team_id
                    )
                )

        conn.commit()
        conn.close()

    def create_collection_rows(self):
        conn = self.connect_database()
        cursor = conn.cursor()

        cursor.execute("SELECT sticker_id FROM stickers")
        stickers = cursor.fetchall()
            
        for row in stickers:
            sticker_id = row["sticker_id"]
            cursor.execute("""INSERT OR IGNORE INTO collection (sticker_id, quantity) VALUES (?, 0)""", (sticker_id,))
        conn.commit()
        conn.close()
    
    def get_sticker_by_code(self, code):
        code = code.strip().upper()
        if not code:
            return None

        conn = self.connect_database()
        cursor = conn.cursor()

        if code:
            cursor.execute("""SELECT 
                stickers.sticker_id,
                stickers.sticker_code,
                stickers.sticker_number,
                stickers.player_name,
                stickers.club,
                stickers.page_number,
                stickers.sticker_type,
                stickers.is_foil,
                teams.team_name,
                teams.fifa_code,
                collection.quantity
                FROM stickers
                JOIN collection 
                    ON stickers.sticker_id = collection.sticker_id
                LEFT JOIN teams
                    ON stickers.team_id = teams.team_id
                WHERE stickers.sticker_code = ? """, (code,))
        
            selected_sticker_info = cursor.fetchone()

        print(selected_sticker_info)
        return(selected_sticker_info)

    def add_sticker(self, code):
        code = code.strip().upper()
        if not code:
            return None
        conn = self.connect_database()
        cursor = conn.cursor()

        if code:
            cursor.execute("""SELECT sticker_id FROM stickers WHERE sticker_code = ? """, (code,))

        sticker = cursor.fetchone()

        if not sticker:
            conn.close()
            return None
        
        sticker_id = sticker["sticker_id"]

        cursor.execute(
        """
        UPDATE collection
        SET quantity = quantity + 1,
            date_updated = CURRENT_TIMESTAMP
        WHERE sticker_id = ?
        """,
        (sticker_id,)
        )

        conn.commit()

        cursor.execute(
            """
            SELECT 
                stickers.sticker_code,
                stickers.player_name,
                teams.team_name,
                collection.quantity
            FROM stickers
            JOIN collection
                ON stickers.sticker_id = collection.sticker_id
            LEFT JOIN teams
                ON stickers.team_id = teams.team_id
            WHERE stickers.sticker_id = ?
            """,
            (sticker_id,)
        )

        updated_sticker = cursor.fetchone()

        conn.close()

        return updated_sticker
    
    def get_missing_stickers(self):

        conn = self.connect_database()
        cursor = conn.cursor()
        cursor.execute("""SELECT 
            stickers.sticker_code,
            stickers.player_name,
            teams.team_name,
            collection.quantity
            FROM stickers
            JOIN collection 
                ON stickers.sticker_id = collection.sticker_id
            LEFT JOIN teams
                ON stickers.team_id = teams.team_id
            WHERE collection.quantity = 0
            """)
        
        missing_stickers = cursor.fetchall()
        for row in missing_stickers:
            print(f"Sticker Code: {row['sticker_code']} | Team Name: {row['team_name']} | Player Name: {row['player_name']}")

        conn.close()

    def get_owned_stickers(self):

        conn = self.connect_database()
        cursor = conn.cursor()
        cursor.execute("""SELECT 
            stickers.sticker_code,
            stickers.player_name,
            teams.team_name,
            collection.quantity
            FROM stickers
            JOIN collection 
                ON stickers.sticker_id = collection.sticker_id
            LEFT JOIN teams
                ON stickers.team_id = teams.team_id
            WHERE collection.quantity >= 1
            """)
        
        owned_stickers = cursor.fetchall()
        for row in owned_stickers:
            print(f"Sticker Code: {row['sticker_code']} | Team Name: {row['team_name']} | Player Name: {row['player_name']} | Quantity: {row['quantity']}")


        conn.close()

    def get_duplicate_stickers(self):

        conn = self.connect_database()
        cursor = conn.cursor()
        cursor.execute("""SELECT 
            stickers.sticker_code,
            stickers.player_name,
            teams.team_name,
            collection.quantity
            FROM stickers
            JOIN collection 
                ON stickers.sticker_id = collection.sticker_id
            LEFT JOIN teams
                ON stickers.team_id = teams.team_id
            WHERE collection.quantity > 1
            """)
        
        duplicate_stickers = cursor.fetchall()
        for row in duplicate_stickers:
            print(f"Sticker Code: {row['sticker_code']} | Team Name: {row['team_name']} | Player Name: {row['player_name']} | Quantity: {row['quantity']}")
        conn.close()

    def get_team_progress(self, team):

        team = team.strip()
        if not team:
            return None
        
        conn = self.connect_database()
        cursor = conn.cursor()
        cursor.execute("""SELECT 
            stickers.sticker_code,
            stickers.player_name,
            teams.team_id,
            teams.team_name,
            teams.fifa_code,
            groups.group_name,
            collection.quantity
            FROM stickers
            JOIN collection 
                ON stickers.sticker_id = collection.sticker_id
            LEFT JOIN teams
                ON stickers.team_id = teams.team_id
            JOIN groups
                ON teams.group_id = groups.group_id
            WHERE teams.team_name = ?""", (team,))
        
        team_stickers = cursor.fetchall()
        for row in team_stickers:
            print(f"Sticker Code: {row['sticker_code']} | Team Name: {row['team_name']} | Player Name: {row['player_name']} | Quantity: {row['quantity']}")
        
        conn.close()
        return team_stickers

        



                


            

        
