# 1. To extract all the texts to the .pot file
    pybabel extract -F babel.cfg -k _l -o messages.pot .

# 2. To create a translation for each language that will be supported in addition to the base one
    pybabel init -i messages.pot -d app/translations -l ru

# 3.
