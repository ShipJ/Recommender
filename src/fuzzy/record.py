class AccountMatch:
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


class ContactMatch:
    def __init__(self
                 , name_status, name_best, name_prob
                 , email_status, email_best, email_prob
                 , account_status, account_best, account_prob
                 , job_status, job_best, job_prob
                 , id_best, action):
        # Name Status
        self.name_status, self.name_best, self.name_prob = name_status, name_best, name_prob
        # Email Status
        self.email_status, self.email_best, self.email_prob = email_status, email_best, email_prob
        # Account Status
        self.account_status, self.account_best, self.account_prob = account_status, account_best, account_prob
        # Job Status
        self.job_status, self.job_best, self.job_prob = job_status, job_best, job_prob
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
        elif record_type == 'Email':
            self.email_status = match_status
            self.email_best = best
            self.email_prob = prob
        elif record_type == 'Account':
            self.account_status = match_status
            self.account_best = best
            self.account_prob = prob
        elif record_type == 'Job':
            self.job_status = match_status
            self.job_best = best
            self.job_prob = prob
