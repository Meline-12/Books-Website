import sqlite3


def create_db():
    """ Creating Book database """

    conn = sqlite3.connect("Book.db")
    cur = conn.cursor()

    cur.executescript(
        """
        PRAGMA foreign_keys = ON;
        
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            year INTEGER,
            isbn TEXT,
            pages INTEGER,
            rating REAL,
            publisher_id INTEGER,
            language_id INTEGER,
            price TEXT,
            description TEXT,
            img TEXT NOT NULL,
            src_id INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE RESTRICT,
            FOREIGN KEY (language_id) REFERENCES languages(id) ON DELETE RESTRICT);

        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            books_count INTEGER,
            rating REAL,
            description TEXT,
            img TEXT NOT NULL,
            src_id INTEGER NOT NULL UNIQUE);

        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            link TEXT NOT NULL UNIQUE);
            
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            link TEXT NOT NULL UNIQUE);
            
        CREATE TABLE IF NOT EXISTS publishers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE);
            
        CREATE TABLE IF NOT EXISTS languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE);
            
        CREATE TABLE IF NOT EXISTS books_authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            type TEXT,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT,
            FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE RESTRICT);
            
        CREATE TABLE IF NOT EXISTS books_genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            genre_id INTEGER NOT NULL,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT,
            FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE RESTRICT);
            
        CREATE TABLE IF NOT EXISTS books_characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            character_id INTEGER,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT,
            FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE RESTRICT);
    
    """
    )

    conn.commit()
    cur.close()
    conn.close()


class SQLBase:
    def __init__(self):
        self.conn = sqlite3.connect("Book.db")
        self.cur = self.conn.cursor()

    def close(self):
        self.conn.close()


class SQLInsert(SQLBase):
    def __init__(self):
        super().__init__()
        self.check = SQLCheck()

    def book(self, value: dict):
        if value["publisher"]:
            self.cur.execute("SELECT id from publishers where name=?", (value["publisher"],))
            publisher_id = self.cur.fetchone()[0]
            value["publisher"] = publisher_id

        if value["language"]:
            self.cur.execute("SELECT id from languages where name=?", (value["language"],))
            language_id = self.cur.fetchone()[0]
            value["language"] = language_id

        if self.check.book(value["src_id"]) is None:
            self.cur.execute("INSERT INTO books (title, year, isbn, pages, rating, publisher_id, language_id, "
                             "price, description, img, src_id) "
                             "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(value.values()))
            self.conn.commit()

    def author(self, value: dict):
        if self.check.author(value["src_id"]) is None:
            self.cur.execute("INSERT INTO authors (name, books_count, rating, description, img, src_id) "
                             "VALUES(?, ?, ?, ?, ?, ?)", tuple(value.values()))
            self.conn.commit()

    def publisher(self, value: str):
        if self.check.publisher(value) is None:
            self.cur.execute("INSERT INTO publishers (name) VALUES(?)", (value,))
            self.conn.commit()

    def language(self, value: str):
        if self.check.language(value) is None:
            self.cur.execute("INSERT INTO languages (name) VALUES(?)", (value,))
            self.conn.commit()

    def character(self, value: dict):
        if self.check.character(value["link"]) is None:
            self.cur.execute("INSERT INTO characters (name, link) VALUES(?, ?)", tuple(value.values()))
            self.conn.commit()

    def genre(self, value: dict):
        if self.check.genre(value["link"]) is None:
            self.cur.execute("INSERT INTO genres (name, link) VALUES(?, ?)", tuple(value.values()))
            self.conn.commit()

    def books_authors(self, book_src_id, author_src_id, author_type):
        self.cur.execute("SELECT id from books where src_id=?", (book_src_id,))
        book_id = self.cur.fetchone()[0]

        self.cur.execute("SELECT id from authors where src_id=?", (author_src_id,))
        author_id = self.cur.fetchone()[0]

        self.cur.execute("INSERT INTO books_authors (book_id, author_id, type) VALUES(?, ?, ?)",
                         (book_id, author_id, author_type))
        self.conn.commit()

    def books_genres(self, book_src_id, genre_link):
        self.cur.execute("SELECT id from books where src_id=?", (book_src_id,))
        book_id = self.cur.fetchone()[0]

        self.cur.execute("SELECT id from genres where link=?", (genre_link,))
        genre_id = self.cur.fetchone()[0]

        self.cur.execute("INSERT INTO books_genres (book_id, genre_id) VALUES(?, ?)",
                         (book_id, genre_id))
        self.conn.commit()

    def books_characters(self, book_src_id, character_link):
        self.cur.execute("SELECT id from books where src_id=?", (book_src_id,))
        book_id = self.cur.fetchone()[0]

        self.cur.execute("SELECT id from characters where link=?", (character_link,))
        character_id = self.cur.fetchone()[0]

        self.cur.execute("INSERT INTO books_characters (book_id, character_id) VALUES(?, ?)",
                         (book_id, character_id))
        self.conn.commit()


class SQLCheck(SQLBase):

    def book(self, src_id: int):
        self.cur.execute("SELECT id from books where src_id=?", (src_id,))
        return self.cur.fetchone()

    def author(self, src_id: int):
        self.cur.execute("SELECT id from authors where src_id=?", (src_id,))
        return self.cur.fetchone()

    def publisher(self, name: str):
        self.cur.execute("SELECT id from publishers where name=?", (name,))
        return self.cur.fetchone()

    def language(self, name: str):
        self.cur.execute("SELECT id from languages where name=?", (name,))
        return self.cur.fetchone()

    def character(self, link: str):
        self.cur.execute("SELECT id from characters where link=?", (link,))
        return self.cur.fetchone()

    def genre(self, link: str):
        self.cur.execute("SELECT id from genres where link=?", (link,))
        return self.cur.fetchone()
