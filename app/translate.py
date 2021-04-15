# import json
# import requests
# from app import translate_client
# from flask_babel import _
# import logging
# import six
#
#
# def translate(text, dest_language):
#
#     if isinstance(text, six.binary_type):
#         text = text.decode("utf-8")
#
#     # Text can also be a sequence of strings, in which case this method
#     # will return a sequence of results for each text.
#     result = translate_client.translate(text, target_language=dest_language)
#     logging.debug(f'result: {result}')
#
#     return result["translatedText"]
