import matplotlib.pyplot as plt
from dbconn import Language

languages = Language()
languages_books = languages.select_all("")

languages = []
books_count = []
other = 0
for language in languages_books[1:]:
    if len(language["books"]) > 7:
        languages.append(language["language"])
        books_count.append(len(language["books"]))
    else:
        other = other + len(language["books"])

languages.append("other")
books_count.append(other)

print(languages)
print(books_count)

fig1, ax1 = plt.subplots(figsize=(11, 10))

ax1.pie(books_count, labels=languages, startangle=90, shadow=True, explode=(0, 0, 0, 0, 0, 0), autopct="%1.2f%%",
        textprops={'fontsize': 16, 'fontweight': "bold"})

# ax1.set_title("CHART FOR BOOK LANGUAGES", fontdict={'fontsize': 16, 'fontweight': "bold"})

total = sum(books_count)
plt.legend(
    loc='upper left',
    labels=['%s, %1.2f%%' % (
        l, (float(s) / total) * 100) for l, s in zip(languages, books_count)],
    prop={'size': 16},
    bbox_to_anchor=(0.0, 0.9),
    bbox_transform=fig1.transFigure
)

ax1.axis("equal")
plt.savefig('languages.png')

plt.show()
