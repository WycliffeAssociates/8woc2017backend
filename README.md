# translation Exchange Backend
A local database to help translators send and access their audio files in an organized and efficient way. The system must be able to operate fully, without any kind of remote internet access. 

## Objective
- The goal of TranslationDB is to be a strong Back-End DBMS for [translationRecorder](https://github.com/WycliffeAssociates/translationRecorder) and [Translation Exchange](https://github.com/WycliffeAssociates/translationExchange).
- The database will be able to interact with the UI using a customized REST API that is running on the local server.
- Store large files in the host machine's *File System*, in order to save on space in the database.

## System Requirements
* 32-bit Operating System (macOS, Windows, Linux)
* Hard Drive or SD Card - **8Gb or more**
* Local Area Netork Connection
   - *Wireless Router - for tablet connectivity*
   - *Wired*
* Localized in English

## Built Using
* [SQLite](https://www.sqlite.org/index.html) - Chosen for Rapid Prototyping and Fast Queries | Built into Django
* [Python 2.7](https://www.python.org/download/releases/2.7/)
* [Django](https://github.com/django/django) - For running a local Web Server
* [Django REST API](http://www.django-rest-framework.org/) - Accessing Django Server from Web & Tablet

### Hardware 
* [Rasberry Pi 2](https://www.raspberrypi.org/products/raspberry-pi-2-model-b/)

## Contributors
This project was made by the *8WoC 2017* intern group.
