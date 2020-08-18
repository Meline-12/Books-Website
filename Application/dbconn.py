from mysql import SQLBase
from abc import ABC, abstractmethod


class Entity(SQLBase, ABC):

    @abstractmethod
    def select_all(self, condition: str):
        pass


class Book(Entity):

    def select_all(self, condition: str):
        self.cur.execute("SELECT name FROM PRAGMA_TABLE_INFO('books')")
        fields = [x[0] for x in self.cur.fetchall()]

        self.cur.execute(f"SELECT * FROM books {condition}")
        books = self.cur.fetchall()

        books_info = []
        for item in books:
            book_info = dict(zip(fields, item))
            del book_info["publisher_id"]
            del book_info["language_id"]

            self.cur.execute(
                "SELECT authors.id, authors.name, books_authors.type FROM authors "
                "INNER JOIN books_authors ON authors.id=books_authors.author_id"
                " WHERE books_authors.book_id=?", (item[0],))

            authors = self.cur.fetchall()
            book_info["author"] = authors

            self.cur.execute("SELECT name FROM languages WHERE id=?", (item[8],))
            language = self.cur.fetchone()
            if language:
                book_info["language"] = language[0]
            else:
                book_info["language"] = None

            self.cur.execute("SELECT name FROM publishers WHERE id=?", (item[7],))
            publisher = self.cur.fetchone()
            if publisher:
                book_info["publisher"] = publisher[0]
            else:
                book_info["publisher"] = None

            books_info.append(book_info)

        return books_info

    def select_by(self, fields: tuple, condition: str, author=None):
        self.cur.execute(f"SELECT {','.join(fields)} FROM books {condition}")
        books = self.cur.fetchall()
        books_info = []
        for book in books:
            book_info = dict(zip(fields, book))

            if author:
                self.cur.execute(
                    "SELECT authors.id, authors.name, books_authors.type FROM authors "
                    "INNER JOIN books_authors ON authors.id=books_authors.author_id"
                    " WHERE books_authors.book_id=?", (book[0],))

                authors = self.cur.fetchall()
                book_info.update({"author": authors})

            books_info.append(book_info)

        return books_info

    def select_characters(self, book_id):
        self.cur.execute(f"SELECT characters.id, characters.name, characters.link from characters "
                         f"INNER JOIN books_characters ON characters.id=books_characters.character_id"
                         f" WHERE books_characters.book_id={book_id}")
        characters = []
        for character in self.cur.fetchall():
            character_info = {}
            character_info["name"] = character[1]
            character_info["link"] = character[2]
            characters.append(character_info)

        return characters

    def select_genres(self, book_id):
        self.cur.execute(f"SELECT genres.id, genres.name from genres "
                         f"INNER JOIN books_genres ON genres.id=books_genres.genre_id"
                         f" WHERE books_genres.book_id={book_id}")
        genres = []
        for genre in self.cur.fetchall():
            genre_info = {}
            genre_info["id"] = genre[0]
            genre_info["name"] = genre[1]
            genres.append(genre_info)

        return genres


class Author(Entity):

    def select_all(self, condition: str):
        self.cur.execute("SELECT name FROM PRAGMA_TABLE_INFO('authors')")
        fields = [x[0] for x in self.cur.fetchall()]

        self.cur.execute(f"SELECT * FROM authors {condition}")
        authors = self.cur.fetchall()

        authors_info = []
        for author in authors:
            author_info = dict(zip(fields, author))
            authors_info.append(author_info)

        return authors_info

    def select_books(self, author_id):
        self.cur.execute(f"SELECT books_authors.book_id FROM books_authors WHERE author_id={author_id}")
        book_ids = self.cur.fetchall()
        books = []
        for id in book_ids:
            b = Book()
            books_info = b.select_by(("id", "title", "year", "average_rating", "rating_count", "img"),
                                     f"WHERE id = {id[0]}", author=True)
            books.extend(books_info)

        return books

    def select_genres(self, author_id):
        books = self.select_books(author_id)
        genres_info = []
        genres_list = []

        for book in books:
            self.cur.execute(
                "SELECT genres.id, genres.name FROM genres INNER JOIN books_genres ON books_genres.genre_id=genres.id "
                "WHERE books_genres.book_id = ?", (book["id"],))
            gen = self.cur.fetchall()
            for genre in gen:
                if genre[1] not in genres_list:
                    genre_info = {}
                    genres_list.append(genre[1])
                    genre_info["id"] = genre[0]
                    genre_info["name"] = genre[1]
                    genres_info.append(genre_info)

        return genres_info


class Character(Entity):

    def select_all(self, condition: str):
        self.cur.execute("SELECT name FROM PRAGMA_TABLE_INFO('characters')")
        fields = [x[0] for x in self.cur.fetchall()]

        self.cur.execute(f"SELECT * FROM characters {condition}")
        characters = self.cur.fetchall()

        characters_info = []
        for character in characters:
            character_info = dict(zip(fields, character))

            book = Book()
            character_info["books"] = book.select_all(
                f"INNER JOIN books_characters ON books.id=books_characters.book_id"
                f" WHERE books_characters.character_id={character[0]}")

            characters_info.append(character_info)

        return characters_info


class Genre(Entity):

    def select_all(self, condition: str):
        self.cur.execute("SELECT name FROM PRAGMA_TABLE_INFO('genres')")
        fields = [x[0] for x in self.cur.fetchall()]

        self.cur.execute(f"SELECT * FROM genres {condition}")
        genres = self.cur.fetchall()

        genres_info = []
        for genre in genres:
            genre_info = dict(zip(fields, genre))

            book = Book()
            genre_info["books"] = book.select_by(("books.id", "books.year"),
                                                 f"INNER JOIN books_genres ON books.id=books_genres.book_id "
                                                 f" WHERE books_genres.genre_id={genre[0]}")

            genres_info.append(genre_info)

        return genres_info

    def select_books(self, genre_id, sort):
        self.cur.execute("SELECT name FROM PRAGMA_TABLE_INFO('genres')")
        fields = [x[0] for x in self.cur.fetchall()]

        self.cur.execute(f"SELECT * FROM genres WHERE genres.id={genre_id}")
        genres = self.cur.fetchall()

        genres_info = []
        for genre in genres:
            genre_info = dict(zip(fields, genre))

            book = Book()
            genre_info["books"] = book.select_by(("books.id", "title", "year", "average_rating", "rating_count", "img"),
                                                 f"INNER JOIN books_genres ON books.id=books_genres.book_id "
                                                 f" WHERE books_genres.genre_id={genre[0]} {sort}", author=True)

            genres_info.append(genre_info)

        return genres_info

    def select_count(self):
        self.cur.execute("SELECT count(*) FROM genres")
        return int(self.cur.fetchone()[0])


class Language(Entity):

    def select_all(self, condition: str):
        self.cur.execute(f"SELECT id, name FROM languages {condition}")
        languages_info = self.cur.fetchall()
        language_books = []
        for language in languages_info:
            language_info = {}
            language_info["language"] = language[1]
            book = Book()
            language_info["books"] = book.select_by(("id", "title"), f"WHERE language_id={language[0]}")
            language_books.append(language_info)

        return language_books


class Publisher(Entity):

    def select_all(self, condition: str):
        self.cur.execute(f"SELECT id, name FROM publishers {condition}")
        publishers_info = self.cur.fetchall()
        publishers_books = []
        for publisher in publishers_info:
            publisher_info = {}
            publisher_info["publisher"] = publisher[1]
            book = Book()
            publisher_info["books"] = book.select_by(("id", "title"), f"WHERE publisher_id={publisher[0]}")
            publishers_books.append(publisher_info)

        return publishers_books
