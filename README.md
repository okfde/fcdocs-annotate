# fcdocs-annotate

## Main concept

The idea behind this application is that users can annotate documents with predefined, customisable features. These features can be e.g: This document is a letter or this document has been redacted. Users have to decide for each document whether it has this feature or not. If there are enough documents with a certain feature (e.g. letters), this feature is done.

For a final annotation, at least two identical annotations from two different users are needed. If there are only two different annotations, a third annotation is needed and the majority decides on the final annotation.

Technically, this means that there are four different tables:

### Documents
we use [django-filingcabinet](https://github.com/okfde/django-filingcabinet)

### Features
The features that can be annotated and how many documents with a certain feature are needed.

### FeatureAnnotationDraft
Annotations created by the user. Users are recognised by session. Each user may only annotate a document/feature combination once. If there are two annotation drafts for the same document/feature combination with the same value (yes or no), a feature annotation is created.

### FeatureAnnotation
Final annotations that can be queried via the API and can be further used.


## Installation

1. Make sure system dependencies are installed. They are defined in [`django-filingcabinet's default.nix`](https://github.com/okfde/django-filingcabinet/blob/master/default.nix).

1.  Clone the Git repository and change into the newly created project directory:

        git clone git@github.com:okfde/fcdocs-annotate.git
        cd fcdocs-annotate

1.  Create a virtual environment:

        python3 -m venv venv

1.  Activate the newly created virtualenv.

        source venv/bin/activate

1.  Set the environment variables. Copy the sample file and edit if needed.

        cp .env-sample .env

1.  Install all dependencies.

        pip install -r requirements.txt

1.  Build frontend

        npm install
        yarn build

1.  Let Django create all required database tables:

        ./manage.py migrate

1.  Create admin user:

        ./manage.py createsuperuser

1.  Start Django's development webserver:

        ./manage.py runserver

1.  Open your browser and browse to localhost:8000
