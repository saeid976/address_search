import time
import zipfile
import pandas as pd
from pathlib import Path
from search.conf.conf import ELASTIC_HOST
from elasticsearch import Elasticsearch, helpers
from concurrent.futures import ThreadPoolExecutor

class ElasticClient:

	def __init__(self, host=ELASTIC_HOST):
		self.host = host
		self.client = None
		self.connect()

	def connect(self):
		falg = False
		while not falg:
			self.client = Elasticsearch(hosts=ELASTIC_HOST, timeout=60)
			if self.client.ping():
				falg = True
			time.sleep(5)

	def dataset_count(self, index_name):
		try:
			dataset_count = self.client.count(index=index_name)
			return dataset_count.raw["count"]
		except Exception as e:
			print(f"Error retrieving dataset count: {e}")
			return None

	def create_index(self, index_name, body):
		try:
			self.client.indices.create(index=index_name, body=body, ignore=400)
		except Exception as e:
			print(f"Warning: Index already exists or an error occurred: {e}")

	def get_index(self):
		try:
			indices = self.client.cat.indices(format="json")
			if indices:
				return True
			else:
				return False
		except Exception as e:
			print(f"Error retrieving schema: {e}")
			return None

	def delete_index(self, index_name):
		try:
			self.client.options(ignore_status=[400,404]).indices.delete(index=index_name)
		except Exception as e:
			print(f"Error deleting index: {e}")

	def process_df(self, row, index_name):
		return {
			"_index": index_name,
			"_source": {
				"place_name": row['place_name'],
				"location": row['location'],
				"address": row['address'],
				"tag": row['tag']
			}
		}

	def bulk_insert(self, actions):
		try:
			helpers.bulk(self.client, actions)
		except Exception as e:
			print(f"Error inserting documents: {e}")

	def process_chunk(self, df_chunk, index_name):
		actions = [self.process_df(row, index_name) for _, row in df_chunk.iterrows()]
		self.bulk_insert(actions)

	def insert_custom(self, df, index_name, num_threads=4, chunk_size=1000):
		try:
			with ThreadPoolExecutor(max_workers=num_threads) as executor:
				for i in range(0, len(df), chunk_size):
					df_chunk = df.iloc[i:i + chunk_size]
					executor.submit(self.process_chunk, df_chunk, index_name)
		except Exception as e:
			print(f"Error inserting custom data: {e}")

	def initiate_database(self, index_name, body):
		
		if not self.get_index():

			print('index is not exists')
			self.create_index(index_name, body)

			zip_path = str(Path(__file__).resolve().parent.joinpath("..", "data.zip").resolve())
			data_directory_path = str(Path(__file__).resolve().parent.joinpath("..", ".").resolve())

			with zipfile.ZipFile(zip_path, 'r') as zip_ref:
				zip_ref.extractall(path=data_directory_path)

			data_path = Path(__file__).resolve().parent.joinpath("..", "data/dataset.csv").resolve()
			df = pd.read_csv(data_path)
			
			self.insert_custom(df, index_name)
			print(f'insert data finished! and it has {self.dataset_count(index_name)} data rows')

		elif self.dataset_count(index_name) == 0:

			print('index is already exists but it is empty!', "\n", "inserting data started")
			self.delete_index(index_name)
			self.create_index(index_name, body)

			zip_path = str(Path(__file__).resolve().parent.joinpath("..", "data.zip").resolve())
			data_directory_path = str(Path(__file__).resolve().parent.joinpath("..", ".").resolve())

			with zipfile.ZipFile(zip_path, 'r') as zip_ref:
				zip_ref.extractall(path=data_directory_path)

			data_path = str(Path(__file__).resolve().parent.joinpath("..", "data/dataset.csv").resolve())
			df = pd.read_csv(data_path)

			self.insert_custom(df, index_name)
			print('insert data finished!')

		else:
			print(f'index is already exists and it has {self.dataset_count(index_name)} data rows')


	def multi_match_search(self, index_name, data):
		try:
			search_query = {
					"query": {
						"bool": {
							"must": [
								{"match": {"place_name": data.place_name}}
							],
							"should": [
								{"match": {"tag": data.tag}}
							],
							"filter": [
								{
									"geo_distance": {
										"distance": "0.2km",
										"location": data.location
									}
								}
							]
						}
					}
				}
			results = self.client.search(index=index_name, body=search_query, size='1000')

			filtered_results = [
				result["_source"] for result in results['hits']['hits']
			]
			return filtered_results

		except Exception as e:
			print(f"Error searching multi match: {e}")
			return None


	def get_all_data(self, index_name):

		try:
			body = {
				"query": {
					"match_all": {}
				}
			}
	
			return self.client.search(index=index_name, body=body, size='10000')
			
		except Exception as e:
			print(f"Error retrieving all data: {e}")
			return None



if __name__ == "__main__":
	conn = ElasticClient()
	print(f"Connection live: {conn.client.ping()}")