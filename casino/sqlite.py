#!/usr/bin/env python

import sqlite3
from datetime import datetime
from time import time

def setup_db(database):
	database.query_stats = {}
	database.db = sqlite3.connect("casino.sqlite", check_same_thread=False)
	database.db.row_factory = row
	database.db.execute("PRAGMA journal_mode = 'WAL'")

def query(self, SQL, values=None, commit=True, allow_large_change=False, log_error=True):
	query_type = SQL.split()[0]
	start = time()
	query_stat = self.query_stats.get(query_type, [0, 0])

	if values is not None and type(values) not in (tuple, list, dict):
		values = (values,)
	
	cursor = self.db.cursor(Cursor)
	try:
		if values is None:
			cursor.execute(SQL)
		else:
			cursor.execute(SQL, values)
	except Exception:
		if log_error:
			self.db.rollback
			print('%s, %s'.format(SQL, values))
		cursor.close()
		
		query_stat[0] += time() - start
		query_stat[1] += 1
		self.query_stats[query_type] = query_stat
		raise
	
	if not SQL.startswith(("INSERT INTO", "INSERT OR IGNORE")) and not allow_large_change and cursor.rowcount > 10:
		self.db.rollback
		cursor.close()
		query_stat[0] += time() - start
		query_stat[1] += 1
		self.query_stats[query_type] = query_stat
		raise RuntimeError("Too many rows affected by change")

	if SQL.startswith(("SELECT", "PRAGMA", "EXPLAIN")) or 'RETURNING' in SQL:
		return_value = cursor
	else:
		return_value = cursor.rowcount
		cursor.close()
		if commit:
			self.db.commit()
	
	query_stat[0] += time() - start
	query_stat[1] += 1
	self.query_stats[query_type] = query_stat

	return return_value

def log_error_to_db(self, error, line):
	self.query("INSERT INTO error_log VALUES(?, ?, ?)", (str(datetime.astimezone(datetime.now())).split('.')[0], error, str(line)))

def like_escape(self, text):
	return text.replace('_', r'\_').replace('%', r'\%')

class CancelReplace:
	pass

class query_iter:
	def __init__(self, cursor):
		self.cursor = cursor
		self.started = False
	def __iter__(self):
		return self
	def __next__(self):
		if not self.started:
			if self.cursor.has_results():
				self.started = True
				return self.cursor.first_result
			raise StopIteration
		row = self.cursor.fetchone()
		if row is None:
			raise StopIteration
		return row

class Cursor(sqlite3.Cursor):
	def __init__(self, *args, **kwargs):
		self.first_result = None
		self.results = None
		super(Cursor, self).__init__(*args, **kwargs)

	def has_results(self):
		if self.first_result is None:
			row = self.fetchone()
			if row is None:
				self.first_result = False
			else:
				self.first_result = row
		return bool(self.first_result)

	def get_results(self):
		if self.results is None:
			if self.has_results():
				self.results = [self.first_result]
				self.results.extend(self.fetchall())
			else:
				self.results = []

	def __bool__(self):
		return self.has_results()

	def __iter__(self):
		if self.results is not None:
			return iter(self.results)
		return query_iter(self)

	def __str__(self):
		self.get_results()
		return str(self.results)

	def __repr__(self):
		self.get_results()
		return repr(self.results)

	def __getitem__(self, item):
		if not self.has_results():
			raise KeyError
		if item == 0:
			return self.first_result
		if type(item) is str:
			return self.first_result[item]
		self.get_results()
		return self.results[item]

	def __len__(self):
		self.get_results()
		return len(self.results)

class row(sqlite3.Row):
	def __str__(self):
		return str(dict(zip(self.keys(), list(self))))
	def __repr__(self):
		return repr(dict(zip(self.keys(), list(self))))