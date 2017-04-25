import json
import requests
import sqlite3
import time
from collections import namedtuple

def get_json_dict():
	while True:
		reddit_response = requests.get('https://www.reddit.com/.json')
		json_loads = json.loads(reddit_response.text)
		if "error" not in json_loads.keys():
			return json_loads

		time.sleep(1)

def collect_data(json_loads):
	children = json_loads['data']['children']
	Post = namedtuple("Post", ["id", "title", "subreddit", "score"])
	list_of_posts = []

	for child in children:
		try:
			data = child['data']
			p = Post(data['id'], data['title'], data['subreddit'], data['score'])
			list_of_posts.append(p)
		except KeyError:
			pass

	return list_of_posts

def already_exists(post, db):
	cursor = db.execute("SELECT COUNT(*) FROM posts where id = ?", [post.id])
	return list(cursor)[0][0] != 0 

def add_to_database(list_of_posts, database_path = 'posts.db'):
	db = sqlite3.connect(database_path)
	for post in list_of_posts:
		if not already_exists(post, db):
			db.execute("INSERT INTO posts VALUES(?,?,?,?);", post)
		else:
			db.execute("UPDATE posts SET score = ? where id = ?", [post.score, post.id])

	db.commit()

def main():
	json_dict = get_json_dict()
	data = collect_data(json_dict)
	add_to_database(data)

if __name__ == '__main__':
	main()
	print("Update Successful")
