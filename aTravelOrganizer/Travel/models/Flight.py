from Travel.models.Travel import Travel

class Flight(Travel):
    def __init__(self, travel_id, datetime, flight_info):
        super().__init__(travel_id, datetime)
        self.info = flight_info
        self.title = "Flight"
        self.status = ""
