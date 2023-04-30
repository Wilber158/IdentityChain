from faker import Faker

class Person:
    def __init__(self, name, dob, gender, ssn, address):
        self.name = name
        self.dob = dob
        self.gender = gender
        self.ssn = ssn
        self.address = address


def get_random_people(num_people=1000):
    fake = Faker()
    people = []

    for _ in range(num_people):
        name = fake.name()
        dob = fake.date_of_birth(tzinfo=None, minimum_age=18, maximum_age=100)
        gender = fake.random_element(elements=('Male', 'Female'))
        ssn = fake.unique.ssn()
        address = fake.address()

        person = Person(name, dob, gender, ssn, address)
        people.append(person)

    return people






