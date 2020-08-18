import matplotlib.pyplot as plt
from dbconn import Genre

genres = Genre()
genres.select("", "")
genres_books = genres.genres_info

genres_books_count = {}
for item in genres_books:
    genres_books_count[item["name"]] = len(item["books"])

# print(genres_books_count)
genres_books_count_sorted = {k: v for k, v in sorted(genres_books_count.items(), key=lambda x: x[1])}

top_5_genres = dict(list(genres_books_count_sorted.items())[-5:])

fig, ax = plt.subplots(figsize=(15, 10))

x = [x for x in top_5_genres.keys()]
y = [y for y in top_5_genres.values()]

# ax.set_title("BOOKS COUNT BY GENRES (top 5)", fontdict={'fontsize': 18, 'fontweight': "bold"})
ax.set_facecolor("coral")
ax.plot(x, y, color="brown")
plt.scatter(x, y, marker="D", c="black")

ax.xaxis.set_tick_params(labelsize=18)
ax.yaxis.set_tick_params(labelsize=18)

plt.savefig("genres.png")

plt.show()
