import sqlite3


def data_cleaning(start, end):
    conn = sqlite3.connect("Book.db")
    cur = conn.cursor()

    for value in range(start, end + 1):
        cur.execute("SELECT id, genre_id FROM books_genres WHERE book_id=?", (value,))
        genre_id = []
        for row in cur.fetchall():
            if row[1] not in genre_id:
                genre_id.append(row[1])
            else:
                cur.execute(f"DELETE FROM books_genres WHERE id={row[0]}")

