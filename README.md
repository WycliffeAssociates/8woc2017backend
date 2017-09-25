# translationDB
A local database to help translators send and access their audio files in an organized and efficient way. The system must be able to operate fully, without any kind of remote internet access. 

## Objective
- The goal of TranslationDB is to be a strong Back-End DBMS for [translationRecorder](https://github.com/WycliffeAssociates/translationRecorder) and a related UI for interfacting with the information on the database.
- The database will be able to interact with the UI using a customized REST API that is running on the local server.
- Store large files in the host machine's "File System", in order to save on space in MongoDB (*and to avoid the 2GB limit on 32-bit machines*)

## Built Using
* [Python 2.7](https://www.python.org/download/releases/2.7/)
* [Django](https://github.com/django/django) - For running a local Web Server
* [Django](http://www.django-rest-framework.org/) - Django REST framework is a powerful and flexible toolkit for building Web APIs.
