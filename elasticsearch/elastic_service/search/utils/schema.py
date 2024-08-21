index_name = 'places'
body = {
	"mappings": {
		"properties": {
			"place_name": {
				"type": "text",
			},
			"location": {
				"type": "geo_point"
			},
			"address": {
				"type": "text"
			},
			"tag": {
				"type": "keyword"
			}
		}
	}
}