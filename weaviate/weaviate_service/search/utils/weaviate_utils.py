import time
import zipfile
import weaviate
import pandas as pd
from pathlib import Path
from geopy.distance import geodesic
from search.conf.conf import Weaviate_HOST


class WeaviateClient:

	def __init__(self, host=Weaviate_HOST):
		self.host = host
		self.client = None
		self.connect()

	def connect(self):
		flag = False
		while not flag:
			self.client = weaviate.Client(self.host)
			if self.client.is_live():
				flag = True
			time.sleep(5)

	def dataset_count(self):
		try:
			dataset_count = (
				self.client.query
				.aggregate("Document")
				.with_meta_count()
				.do()
				["data"]["Aggregate"]["Document"][0]["meta"]["count"]
			)
			return dataset_count
		except Exception as e:
			print(f"Error retrieving dataset count: {e}")
			return None

	def create_schema(self, schema: dict):
		try:
			self.client.schema.create({"classes": [schema]})
		except Exception as e:
			print(f"Warning: Schema already exists or an error occurred: {e}")

	def get_schema(self):
		try:
			response = self.client.schema.get()
			print("response for get schema", response)
			return response
		except Exception as e:
			print(f"Error retrieving schema: {e}")
			return None

	def delete_schema(self, schema: dict):
		try:
			self.client.schema.delete_class(schema)
		except Exception as e:
			print(f"Error deleting schema: {e}")

	def insert_custom(self, df, batch_size=1000):
		try:
			def convert_location_str_to_geo_coordinates(location_str):
				lat, lon = map(float, location_str.split(","))
				return {
					"latitude": lat,
					"longitude": lon
				}

			df['location'] = df['location'].apply(convert_location_str_to_geo_coordinates)

			with self.client.batch as batch:
				batch.batch_size = 1000
				for i, data in df.iterrows():
					if i % 100 == 0:
						print(f"Importing place: {i}")
					properties = {
						"place_name": data["place_name"],
						"location": data["location"],
						"address": data["address"],
						"tag": data["tag"]
					}
					self.client.batch.add_data_object(properties, "Document")
		except Exception as e:
			print(f"Error inserting custom data: {e}")


	def initiate_database(self, schema):
		self.create_schema(schema)
		if not self.get_schema():

			print('schema is not exists')
			self.create_schema(schema)

			zip_path = str(Path(__file__).resolve().parent.joinpath("..", "data.zip").resolve())
			data_directory_path = str(Path(__file__).resolve().parent.joinpath("..", ".").resolve())

			with zipfile.ZipFile(zip_path, 'r') as zip_ref:
				zip_ref.extractall(path=data_directory_path)

			data_path = Path(__file__).resolve().parent.joinpath("..", "data/dataset.csv").resolve()
			df = pd.read_csv(data_path)
			
			self.insert_custom(df, schema)
			print(f'insert data finished! and it has {self.dataset_count()} data rows')

		elif self.dataset_count() == 0:

			print('schema is already exists but it is empty!', "\n", "inserting data started")
			self.delete_schema("Document")

			zip_path = str(Path(__file__).resolve().parent.joinpath("..", "data.zip").resolve())
			data_directory_path = str(Path(__file__).resolve().parent.joinpath("..", ".").resolve())

			with zipfile.ZipFile(zip_path, 'r') as zip_ref:
				zip_ref.extractall(path=data_directory_path)

			data_path = str(Path(__file__).resolve().parent.joinpath("..", "data/dataset.csv").resolve())
			df = pd.read_csv(data_path)

			self.insert_custom(df, schema)
			print(f'insert data finished! and it has {self.dataset_count()} data rows')

		else:
			print(f'schema is already exists and it has {self.dataset_count()} data rows')


	def search_near_geo_raw(self, class_name, data, max_distance = 500):
		try:
			query = f"""
			{{
			Get {{
				{class_name}(
				where: {{
					operator: And,
					operands: [
					{{
						operator: Equal,
						path: ["place_name"],
						valueText: "{data.place_name}"
					}},
					{{
						operator: WithinGeoRange,
						valueGeoRange: {{
						geoCoordinates: {{
							latitude: {data.location.latitude},
							longitude: {data.location.longitude}
						}},
						distance: {{
							max: {max_distance}
						}}
						}},
						path: ["location"]
					}}
					]
				}}
				) {{
				place_name
				address
				location {{
					latitude
					longitude
				}}
				tag
				}}
			}}
			}}
			"""
			results = self.client.query.raw(query)
			filtered_results = [
				result for result in results.get("data", {}).get("Get", {}).get(class_name, [])
			]
			return filtered_results
		except Exception as e:
			print(f"Error executing raw query: {e}")
			return None

	def search_bm25(self, class_name, data, score_threshold=0.99):
		try:
			place_name = data.place_name
			address = data.address
			text = f"{place_name}, {address}"
			results = (
				self.client.query
				.get(class_name, ["place_name", "location", "tag"])
				.with_bm25(
					query=text,
					properties=["place_name^7", "tag"]
				)
				.with_additional("score")
				.with_limit(10000).do()
			)

			searched_loc = data.location

			def geo_similarity(loc1, loc2):
				loc1 = tuple(map(float, loc1.split(',')))
				loc2 = tuple(map(float, loc2.split(',')))
				distance = geodesic(loc1, loc2).kilometers
				return distance < 1

			filtered_results = [
				result for result in results.get("data", {}).get("Get", {}).get(class_name, [])
				if float(result["_additional"]["score"]) >= score_threshold
				and geo_similarity(searched_loc, result["location"])
			]

			return filtered_results

		except Exception as e:
			print(f"Error in BM25 search: {e}")
			return None


	def get_all_data(self, class_name):
		try:
			return (
				self.client.query
				.get(class_name, ["place_name", "location"])
				.do()
			)
		except Exception as e:
			print(f"Error retrieving all data: {e}")
			return None

	def search_near_vector(self, class_name, vec, fields, certainty=0.8):
		try:
			vec_content = {'vector': vec, 'certainty': certainty}
			return self.client.query.get(class_name, fields).with_near_vector(vec_content).do()
		except Exception as e:
			print(f"Error in vector search: {e}")
			return None


if __name__ == "__main__":
	conn = WeaviateClient()
	print(f"Connection live: {conn.client.is_live()}")