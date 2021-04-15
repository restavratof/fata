# 1. To extract all the texts to the .pot file
    pybabel extract -F babel.cfg -k _l -o messages.pot .

# 2. To create a translation for each language that will be supported in addition to the base one
    pybabel init -i messages.pot -d app/translations -l ru

# 3. This operation adds a messages.mo file next to messages.po in each language repository
    pybabel compile -d app/translations

# 4. Updating the Translations
    pybabel extract -F babel.cfg -k _l -o messages.pot .
    pybabel update -i messages.pot -d app/translations
