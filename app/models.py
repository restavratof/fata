class City(object):
    def __init__(self, name, state, country, capital=False, population=0, regions=[]):
        self.name = name
        self.state = state
        self.country = country
        self.capital = capital
        self.population = population
        self.regions = regions

    @staticmethod
    def from_dict(source):
        # ...
        pass

    def to_dict(self):
        # ...
        pass

    def __repr__(self):
        return(
            f'City(\
                name={self.name}, \
                country={self.country}, \
                population={self.population}, \
                capital={self.capital}, \
                regions={self.regions}\
            )'
        )

cities_ref = db.collection(u'cities')
cities_ref.document(u'BJ').set(
    City(u'Beijing', None, u'China', True, 21500000, [u'hebei']).to_dict())
cities_ref.document(u'SF').set(
    City(u'San Francisco', u'CA', u'USA', False, 860000,
         [u'west_coast', u'norcal']).to_dict())
cities_ref.document(u'LA').set(
    City(u'Los Angeles', u'CA', u'USA', False, 3900000,
         [u'west_coast', u'socal']).to_dict())
cities_ref.document(u'DC').set(
    City(u'Washington D.C.', None, u'USA', True, 680000,
         [u'east_coast']).to_dict())
cities_ref.document(u'TOK').set(
    City(u'Tokyo', None, u'Japan', True, 9000000,
         [u'kanto', u'honshu']).to_dict())

