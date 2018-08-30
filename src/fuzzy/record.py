class Record:
    def __init__(self
                 , name_status, name_best, name_prob
                 , address_status, address_best, address_prob
                 , id_best, action):
        # Name Status
        self.name_status, self.name_best, self.name_prob = name_status, name_best, name_prob
        # Address Status
        self.address_status, self.address_best, self.address_prob = address_status, address_best, address_prob
        # Index of Best Match, Action to Take
        self.id_best, self.action = id_best, action

    def update_id_action(self, id_best, action):
        self.id_best = id_best
        self.action = action

    def toggle(self, record_type, match_status, best, prob):
        if record_type == 'Name':
            self.name_status = match_status
            self.name_best = best
            self.name_prob = prob
        elif record_type == 'Address':
            self.address_status = match_status
            self.address_best = best
            self.address_prob = prob
