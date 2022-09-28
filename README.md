# fcdocs-annotate

## Main concept

The idea behind this application is that users can annotate documents with predefined, customisable features. These features can be e.g: This document is a letter or this document has been redacted. Users have to decide for each document whether it has this feature or not. If there are enough documents with a certain feature (e.g. letters), this feature is done.

For a final annotation, at least two identical annotations from two different users are needed. If there are only two different annotations, a third annotation is needed and the majority decides on the final annotation.

Technically, this means that there are four different tables:

### Documents
We use [django-filingcabinet](https://github.com/okfde/django-filingcabinet).
Refer there for installation instructions.

### Features
The features that can be annotated and how many documents with a certain feature are needed.

### FeatureAnnotationDraft
Annotations created by the user. Users are recognised by session. Each user may only annotate a document/feature combination once. If there are two annotation drafts for the same document/feature combination with the same value (yes or no), a feature annotation is created.

### FeatureAnnotation
Final annotations that can be queried via the API and can be further used.
