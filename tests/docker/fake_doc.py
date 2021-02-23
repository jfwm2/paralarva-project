import json
from faker import Faker

if __name__ == '__main__':
    fake = Faker()
    print(json.dumps({
        'email': fake.email(),
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'prefix': fake.prefix(),
        'building_number': fake.building_number(),
        'city': fake.city(),
        'city_suffix': fake.city_suffix(),
        'country': fake.country(),
        'country_code': fake.country_code(),
        'postcode': fake.postcode(),
        'street_name': fake.street_name(),
        'street_suffix': fake.street_suffix(),
        'bank_country': fake.bank_country(),
        'bban': fake.bban(),
        'iban': fake.iban(),
        'swift11': fake.swift11(),
        'swift8': fake.swift8(),
        'credit_card_expire': fake.credit_card_expire(),
        'credit_card_number': fake.credit_card_number(),
        'credit_card_provider': fake.credit_card_provider(),
        'credit_card_security_code': fake.credit_card_security_code(),
        'job': fake.job(),
        'sentence': fake.sentence(),
        'text': fake.text(),
        'paragraphs': fake.paragraphs(),
        'country_calling_code': fake.country_calling_code(),
        'msisdn': fake.msisdn(),
        'phone_number': fake.phone_number(),
        'user_agent': fake.user_agent(),
        'currency_code': fake.currency_code(),
        'currency_name': fake.currency_name(),
        'currency_symbol': fake.currency_symbol(),
        'texts': fake.texts(nb_texts=5, max_nb_chars=1024)
    }))
