from collections import defaultdict
from datetime import datetime, timedelta


class DataAggregator:
    def __init__(self, ttl_minutes=1):
        self.cache = defaultdict(dict)
        self.ttl = timedelta(minutes=ttl_minutes)

    def add_data(self, accident_id, data_type, data):
        self._cleanup()
        self.cache[accident_id][data_type] = {
            'data': data,
            'timestamp': datetime.now()
        }
        return self.check_ready(accident_id)
    
    def check_ready(self, accident_id):
        return all(t in self.cache[accident_id] for t in ['accident', 'road'])
    
    def get_combined_data(self, accident_id):
        combined = {}
        for data_type in ['accident', 'road']:
            combined.update(self.cache[accident_id][data_type]['data'])
        del self.cache[accident_id]
        return combined
    
    def _cleanup(self):
        now = datetime.now()
        expired = [k for k, v in self.cache.items() 
                 if (now - max(entry['timestamp'] for entry in v.values())) > self.ttl]
        for k in expired:
            del self.cache[k]
            