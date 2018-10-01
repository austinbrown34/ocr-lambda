# ocr-lambda

## Getting Started

These instructions will get you a copy of the project up and running on AWS Lambda.

### Prerequisites

Before you begin, make sure you are running Python 2.7 or Python 3.6 and you have a valid AWS account and your AWS credentials file is properly installed. Please note that DoParallel must be installed into your project's virtual environment.


### Installing

1. Clone git@github.com:law360/ocr-lambda.git

```
git clone git@github.com:law360/ocr-lambda.git
```

2. Create a virtual environment in this directory.

```
virtualenv env
```

3. Activate your virtual environment.

```
. env/bin/activate
```

4. Install Requirements

```
pip install -r requirements.txt
```

5. Initialize Zappa and Follow Instructions

```
zappa init
```

6. Deploy Zappa

```
zappa deploy
```

### Usage

Coming soon...
