from dbconn import Book, Author, Character, Genre
from flask import Flask, render_template, request

app = Flask(__name__)


def pagination(page: int, items_per_page: int, len_info: int):
    """ for pagination / In many cases we use OFFSET, LIMIT,
    but in the authors' page we use this function for variety """

    pages = round(len_info / items_per_page + .499)  # the .499 is for rounding to the upside
    from_page = page * items_per_page - items_per_page  # 36 per page
    upto_page = page * items_per_page

    page_info = {"pages": pages, "from_page": from_page, "upto_page": upto_page}

    return page_info


@app.route("/")
def home():
    book = Book()
    top_books = book.select_by(
        ("id", "title", "year", "average_rating", "rating_count", "img"),
        "ORDER BY rating_count DESC, average_rating DESC LIMIT 10", author=True)

    return render_template("home.html", top_books=top_books)


@app.route("/books/<book_id>")
def book(book_id):
    book = Book()
    info = book.select_all(f"WHERE books.id={book_id}")[0]

    characters = book.select_characters(book_id)
    genres = book.select_genres(book_id)

    return render_template("book.html", info=info, characters=characters, genres=genres)


@app.route("/books/<page>/")
def books(page=1):
    book = Book()

    page = int(page)
    items_per_page = 10
    values = {"limit": items_per_page, "offset": (page - 1) * items_per_page}
    pages = round(10000 / items_per_page + .499)
    list_part = book.select_by(("id", "title", "year", "average_rating", "rating_count", "img"),
                               f"LIMIT {values['limit']} OFFSET {values['offset']}", author=True)

    sort = request.args.get("query", "").strip()
    if sort == "year":
        books_sort_by_year = Book()
        list_part = books_sort_by_year.select_by(("id", "title", "year", "average_rating", "rating_count", "img"),
                                                 f"ORDER BY year DESC LIMIT {values['limit']} OFFSET {values['offset']}",
                                                 author=True)
        return render_template("books.html", list_part=list_part, pages=pages, page=page)

    if sort == "rating":
        books_sort_by_rating = Book()
        list_part = books_sort_by_rating.select_by(("id", "title", "year", "average_rating", "rating_count", "img"),
                                                   f"ORDER BY rating_count DESC LIMIT {values['limit']} OFFSET {values['offset']}",
                                                   author=True)
        return render_template("books.html", list_part=list_part, pages=pages, page=page)

    return render_template("books.html", list_part=list_part, pages=pages, page=page)


@app.route("/search/")
def search():
    book = Book()
    author = Author()
    character = Character()
    query = request.args.get("query", None)
    if query:
        books = book.select_all("WHERE upper(title) LIKE " f"'%{query.upper()}%'")
        isbn_books = book.select_all("WHERE isbn LIKE " f"'%{query}%'")
        if isbn_books:
            books.append(isbn_books)

        authors = author.select_all("WHERE upper(name) LIKE " f"'%{query.upper()}%'")
        characters = character.select_all("WHERE upper(name) LIKE " f"'%{query.upper()}%'")

        return render_template("search.html", books=books, authors=authors, characters=characters)

    return render_template("search.html")


@app.route("/authors/<author_id>")
def author(author_id):
    author = Author()
    info = author.select_all(f"WHERE id={author_id}")[0]
    genres = author.select_genres(author_id)
    books_count = len(author.select_books(author_id))

    return render_template("author.html", info=info, genres=genres, books_count=books_count)


@app.route("/authors/<page>/")
def displayitem(page=1):
    authors = Author()
    author = authors.select_all("")

    page = int(page)
    page_info = pagination(page, 10, len(author))
    list_part = author[page_info["from_page"]:page_info["upto_page"]]
    pages = page_info["pages"]

    sort = request.args.get("query", "").strip()
    if sort == "books_count":
        authors_sort_by_count = Author()
        info_by_count = authors_sort_by_count.select_all("ORDER BY books_count DESC")
        list_part = info_by_count[page_info["from_page"]:page_info["upto_page"]]
        return render_template("authors.html", list_part=list_part, pages=pages, page=page)

    if sort == "rating":
        authors_sort_by_rating = Author()
        info_by_rating = authors_sort_by_rating.select_all("ORDER BY rating_count DESC")
        list_part = info_by_rating[page_info["from_page"]:page_info["upto_page"]]
        return render_template("authors.html", list_part=list_part, pages=pages, page=page)

    return render_template("authors.html", list_part=list_part, pages=pages, page=page)


@app.route("/authors/<author_id>/<count>")
def displaybooks(author_id, count):
    authors = Author()
    author = authors.select_all(f"WHERE id={author_id}")[0]
    books = authors.select_books(author_id)

    return render_template("authorbook.html", books=books, author=author)


@app.route("/genres")
def genres():
    genre = Genre()

    page = int(request.args.get("page", 1))
    items_per_page = 30
    values = {'limit': items_per_page, 'offset': (page - 1) * items_per_page}

    list_part = genre.select_all(f"LIMIT {values['limit']} OFFSET {values['offset']}")
    pages_count = genre.select_count()
    pages = round(pages_count / items_per_page + .499)

    query = request.args.get("query", None)
    if query:
        search_genre = Genre()
        search_info = search_genre.select_all("WHERE upper(genres.name) LIKE " f"'%{query.upper()}%'")
        return render_template("genres.html", list_part=list_part, pages=pages, page=page, search_info=search_info)

    return render_template("genres.html", list_part=list_part, pages=pages, page=page)


@app.route("/genres/<genre_id>/")
def genre(genre_id):
    genre = Genre()
    info_genre = genre.select_books(genre_id, "")[0]
    pages_count = len(info_genre["books"])

    page = int(request.args.get("page", 1))
    items_per_page = 10
    pages = round(pages_count / items_per_page + .499)
    values = {"limit": items_per_page, "offset": (page - 1) * items_per_page}

    info_books = genre.select_books(genre_id, f"LIMIT {values['limit']} OFFSET {values['offset']}")[0]["books"]

    sort = request.args.get("query", "").strip()
    if sort == "year":
        genre_sort_by_year = Genre()
        info_books = genre_sort_by_year.select_books(genre_id,
                                                     f"ORDER BY books.year DESC LIMIT {values['limit']}"
                                                     f" OFFSET {values['offset']}")[0]["books"]
        return render_template("genre.html", info=info_genre, books=info_books, pages=pages, page=page)

    if sort == "rating":
        genre_sort_by_rating = Genre()
        info_by_rating = genre_sort_by_rating.select_books(genre_id,
                                                           f"ORDER BY books.rating_count DESC, books.average_rating DESC "
                                                           f"LIMIT {values['limit']} OFFSET {values['offset']}")[0][
            "books"]
        return render_template("genre.html", info=info_by_rating, books=info_books, pages=pages, page=page)

    return render_template("genre.html", info=info_genre, books=info_books, pages=pages, page=page)


@app.route("/interesting_facts")
def interesting_facts():
    return render_template("interesting_facts.html")
