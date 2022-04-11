import pytest
from annotation.models import Feature, FeatureAnnotation


@pytest.mark.django_db
def test_annotate_view(client, document_factory, feature_factory, formset_data):

    d1 = document_factory(public=True)
    d2 = document_factory(public=True)
    d3 = document_factory(public=True)

    f1 = feature_factory(documents_needed=1)
    f2 = feature_factory()

    data = formset_data(formdata=[(f1.id, d1.id, True), (f2.id, d1.id, False)])

    response = client.post("/annotate/", data, follow=True)
    assert response.context_data.get("object") == d2
    assert response.context_data.get("progress") == 33
    formset = response.context_data.get("feature_form_set")
    assert len(formset.initial) == 2
    assert formset.initial[0].get("document") == d2.id
    assert formset.initial[0].get("feature") == f1.id
    assert formset.initial[1].get("document") == d2.id
    assert formset.initial[1].get("feature") == f2.id
    assert client.session["annotated_documents"] == [d1.id]

    data = formset_data(formdata=[(f1.id, d2.id, False), (f2.id, d2.id, True)])

    response = client.post("/annotate/", data, follow=True)
    assert response.context_data.get("object") == d3
    assert response.context_data.get("progress") == 66
    formset = response.context_data.get("feature_form_set")
    assert len(formset.initial) == 2
    assert formset.initial[0].get("document") == d3.id
    assert formset.initial[0].get("feature") == f1.id
    assert formset.initial[1].get("document") == d3.id
    assert formset.initial[1].get("feature") == f2.id
    assert client.session["annotated_documents"] == [d1.id, d2.id]

    data = formset_data(formdata=[(f1.id, d3.id, True), (f2.id, d3.id, True)])

    response = client.post("/annotate/", data, follow=True)
    assert not response.context_data.get("object")
    assert response.context_data.get("progress") == 100
    assert not response.context_data.get("feature_form_set")
    assert client.session["annotated_documents"] == [d1.id, d2.id, d3.id]

    assert FeatureAnnotation.objects.filter(final=True).count() == 0
    assert Feature.objects.annotation_needed().count() == 2

    session = client.session
    session["annotated_documents"] = [d1.id, d2.id]
    session.save()

    assert session["annotated_documents"] == [d1.id, d2.id]

    response = client.get("/annotate/")
    assert response.context_data.get("object") == d3
    assert response.context_data.get("progress") == 66

    data = formset_data(formdata=[(f1.id, d3.id, True), (f2.id, d3.id, True)])
    response = client.post("/annotate/", data, follow=True)

    assert FeatureAnnotation.objects.filter(final=True).count() == 2
    assert Feature.objects.annotation_needed().count() == 1
