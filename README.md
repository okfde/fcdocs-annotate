# fcdocs-annotate

## Installation

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

1.  Let Django create all required database tables:

        cd fcdocs_annotate
        ./manage.py migrate

1.  Start Django's development webserver:

        ./manage.py runserver
