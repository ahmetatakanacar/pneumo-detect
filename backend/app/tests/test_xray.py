def test_upload_xray_as_doctor_succeeds(test_client, auth_headers, sample_image):
    headers = auth_headers(role="doctor")

    with open(sample_image, "rb") as f:
        response = test_client.post(
            "/upload-xray",
            headers=headers,
            files={"file": (sample_image.name, f, "image/jpeg")},
        )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["result"] in ("NORMAL", "PNEUMONIA")
    assert 0.0 <= body["confidence"] <= 1.0

def test_upload_xray_as_readonly_is_forbidden(test_client, auth_headers, sample_image):
    headers = auth_headers(role="readonly")

    with open(sample_image, "rb") as f:
        response = test_client.post(
            "/upload-xray",
            headers=headers,
            files={"file": (sample_image.name, f, "image/jpeg")},
        )

    assert response.status_code == 403

def test_upload_xray_rejects_non_image_content_type(test_client, auth_headers):
    headers = auth_headers(role="doctor")

    response = test_client.post(
        "/upload-xray",
        headers=headers,
        files={"file": ("note.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400

def test_get_result_returns_previously_created_result(test_client, auth_headers, sample_image):
    headers = auth_headers(role="admin")

    with open(sample_image, "rb") as f:
        upload_response = test_client.post(
            "/upload-xray",
            headers=headers,
            files={"file": (sample_image.name, f, "image/jpeg")},
        )
    result_id = upload_response.json()["id"]

    response = test_client.get(f"/get-result/{result_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == result_id

def test_get_result_returns_404_for_unknown_id(test_client, auth_headers):
    headers = auth_headers()
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = test_client.get(f"/get-result/{fake_id}", headers=headers)
    assert response.status_code == 404