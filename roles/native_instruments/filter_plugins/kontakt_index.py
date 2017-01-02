def kontakt_index(index):
    return {'UserListIndex': index}

class FilterModule(object):
    def filters(self):
        return {'kontakt_index': kontakt_index}
