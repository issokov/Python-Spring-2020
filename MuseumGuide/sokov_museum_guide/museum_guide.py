from collections import defaultdict


class MuseumGuide:
    def __init__(self, db):
        self.db = db

    def find_authors(self, author: str):
        cursor = self.db.exhibits.find({
            "$text": {
                "$search": author,
                "$language": "ru"
            }
        })
        authors_id = set()
        for item in cursor:
            for i, cand_aut in enumerate(item["authors"]):
                if author in cand_aut:
                    authors_id.add(item["authors_id"][i])

        return list(authors_id)

    def find_museums(self, authors):
        museums_counter = defaultdict(lambda: 0)
        aggregated_museums = self.db.exhibits.aggregate([
            {"$match": {"authors_id": {"$in": authors}}},
            {"$group": {
                "_id": "$museum_id",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ])
        # 2020-04-03 Ruslan Nasonov: группировку лучше сделать на уровне базы
        # исправлено
        for museum_count_pr in aggregated_museums:
            museums_counter[museum_count_pr["_id"]] = museum_count_pr["count"]
        return museums_counter

    def get_exhibits_gen(self, museum_id, authors_ids):
        cursor = self.db.exhibits.find({"authors_id": {"$elemMatch": {"$in": authors_ids}}, "museum_id": museum_id})
        for exhibit in cursor:
            yield exhibit

    def create_tour(self, museums_counts):
        buckets, handled = [], defaultdict(lambda: False)
        museums_counts.sort(key=lambda x: x[1], reverse=True)
        museums_counts = dict(museums_counts)
        museums = list(museums_counts.keys())
        for head in museums:
            if not handled[head]:
                handled[head] = True
                bucket = [self.db.museums.find_one({"_id": head})]
                count = museums_counts[head]
                bucket[0]["count"] = count
                location = bucket[0]["location"]
                nearest = self.db.museums.find({
                    "location": {
                        "$geoNear": {
                            "$geometry": location,
                            "$maxDistance": 100000,
                            "$minDistance": 0
                        }
                    },
                    "_id": {"$in": museums}
                })
                for museum in nearest:
                    if not handled[museum["_id"]]:
                        count_in = museums_counts[museum["_id"]]
                        museum["count"] = count_in
                        bucket.append(museum)
                        count += count_in
                        handled[museum["_id"]] = True
                buckets.append((bucket, count))
        buckets.sort(key=lambda x: x[1], reverse=True)
        return buckets
