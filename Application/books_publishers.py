import matplotlib.pyplot as plt
from dbconn import Publisher

publishers = Publisher()
publishers_books = publishers.select_all("")

publishers_books_count = {}
for item in publishers_books:
    publishers_books_count[item["publisher"]] = len(item["books"])

publishers_books_count_sorted = {k: v for k, v in sorted(publishers_books_count.items(), key=lambda x: x[1])}

top_5_publishers = dict(list(publishers_books_count_sorted.items())[-5:])

fig, ax = plt.subplots(figsize=(22, 13))

bar = ax.bar(top_5_publishers.keys(), top_5_publishers.values(), align='center')
ax.set_xticklabels(top_5_publishers.keys())
ax.set_ylabel("Books count", fontdict={'fontsize': 20, 'fontweight': "bold"})
# ax.set_title("BOOKS COUNT BY PUBLISHER (top 5)", fontdict={'fontsize': 18, 'fontweight': "bold"})

ax.xaxis.set_tick_params(labelsize=18)
ax.yaxis.set_tick_params(labelsize=18)

for rect in bar:
    height = rect.get_height()
    plt.text(rect.get_x() + rect.get_width() / 2., 1.01 * height, '%d' % int(height),
             ha='center', va='bottom', fontdict={'fontsize': 18, 'fontweight': "bold"})

plt.savefig("publishers.png")

plt.show()
