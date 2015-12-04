from Travel.models.Travel import Travel

class Place(Travel):
    def __init__(self, travel_id, datetime, place_info):
        super().__init__(travel_id, datetime)
        self.info = place_info
        self.title="Place"
