from httpx import AsyncClient
from fastapi import status

from tests.tests_api.conftest import get_document_url


class TestDocument:

    async def test_my_documents_unauthorized(self, client: AsyncClient):
        response = await client.get(get_document_url("my_documents"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Auth credentials are not provided.'}

    async def test_my_documents_success(self, client_user1: AsyncClient, documents_test_data):
        response = await client_user1.get(get_document_url("my_documents"))
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        single_document = data[0]
        assert single_document["title"] == "python"
        assert single_document['extension'] == "pdf"
        assert single_document['pages'] == 100
        assert single_document["current_page"] == 0

    async def test_get_document(self, client_user1: AsyncClient, documents_test_data):
        document_id = documents_test_data['_id']
        response = await client_user1.get(get_document_url("document_get", document_id=document_id))
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['title'] == "python"
        assert data["extension"] == "pdf"
        assert data["pages"] == 100
        assert data["current_page"] == 0
        assert data['_id'] == document_id
        assert "user_id" in data
        assert "document_url" in data
        assert "cover_url" in data

    async def test_document_upload_success(self, client_user1: AsyncClient, documents_test_data):
        with open("tests/tests_api/files/c#.pdf", "rb") as file:
            response = await client_user1.post(
                get_document_url("upload_document"),
                files={"document_file": file}
            )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['title'] == "c#"
        assert data["extension"] == "pdf"
        assert data["pages"] == 772
        assert data["current_page"] == 0
        assert "_id" in data
        assert "user_id" in data
        assert "document_url" in data
        assert "cover_url" in data
        document_id = data['_id']

        my_documents_new_response = await client_user1.get(get_document_url("my_documents"))
        assert len(my_documents_new_response.json()) == 2

        file_response = await client_user1.get(get_document_url("document_get", document_id=document_id))
        assert file_response.status_code == status.HTTP_200_OK

        file_data = file_response.json()
        assert file_data['title'] == "c#" == data['title']
        assert file_data["extension"] == "pdf" == data['extension']
        assert file_data["pages"] == 772 == data['pages']
        assert file_data["current_page"] == 0 == data['current_page']
        assert "_id" in file_data and file_data['_id'] == data['_id']
        assert "user_id" in file_data and file_data['user_id'] == data['user_id']
        assert "document_url" in file_data and file_data['document_url'] == data['document_url']
        assert "cover_url" in file_data and file_data['cover_url'] == data['cover_url']

    async def test_document_upload_fail_extension(self, client_user1: AsyncClient, documents_test_data):
        with open("tests/tests_api/conftest.py", "rb") as file:
            response = await client_user1.post(
                get_document_url("upload_document"),
                files={"document_file": file}
            )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "py not in available extensions: `pdf`."}

        my_documents_new_response = await client_user1.get(get_document_url("my_documents"))
        assert len(my_documents_new_response.json()) == 1

    async def test_document_download(self, client_user1: AsyncClient, documents_test_data):
        document_id = documents_test_data['_id']

        response = await client_user1.post(
            get_document_url("download_document", document_id=document_id)
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.content

    async def test_document_delete_success(self, client_user1: AsyncClient, documents_test_data):
        document_id = documents_test_data['_id']
        response = await client_user1.delete(
            get_document_url("document_delete", document_id=document_id)
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"detail": f"Document {document_id} is deleted."}

        my_documents_new_response = await client_user1.get(get_document_url("my_documents"))
        assert not len(my_documents_new_response.json())

    async def test_document_delete_already_deleted(self, client_user1: AsyncClient, documents_test_data):
        document_id = documents_test_data['_id']
        response1 = await client_user1.delete(
            get_document_url("document_delete", document_id=document_id)
        )
        assert response1.status_code == status.HTTP_200_OK
        assert response1.json() == {"detail": f"Document {document_id} is deleted."}

        my_documents_new_response1 = await client_user1.get(get_document_url("my_documents"))
        assert not len(my_documents_new_response1.json())

        document_id = documents_test_data['_id']
        response2 = await client_user1.delete(
            get_document_url("document_delete", document_id=document_id)
        )
        assert response2.status_code == status.HTTP_200_OK
        assert response2.json() == {"detail": "Document is already deleted."}

        my_documents_new_response2 = await client_user1.get(get_document_url("my_documents"))
        assert not len(my_documents_new_response2.json())

    async def test_document_not_found(self, client_user1: AsyncClient):
        document_id = "885f47d9-ecc5-4a67-b197-108cd7ce5401"
        response = await client_user1.get(get_document_url("document_get", document_id=document_id))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Document is not found."}

    async def test_document_update(self, client_user1: AsyncClient, documents_test_data):
        document_id = documents_test_data['_id']
        update_data = {
            'title': "Python 3.11"
        }
        response = await client_user1.patch(
            get_document_url("document_update", document_id=document_id),
            json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"detail": f"Document {document_id} is updated."}

        response_get = await client_user1.get(get_document_url("document_get", document_id=document_id))
        assert response_get.status_code == status.HTTP_200_OK
        data = response_get.json()
        assert data['title'] == update_data['title']

    async def test_document_text_on_page(self, client_user1: AsyncClient, documents_test_data):
        document_id = documents_test_data['_id']
        response = await client_user1.get(
            get_document_url("get_document_text", document_id=document_id) + "?page=87",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "text" in data and isinstance(data['text'], str)

    async def test_document_text_on_page_out_of_range_positive(self, client_user1: AsyncClient, documents_test_data):
        document_id = documents_test_data['_id']
        response = await client_user1.get(
            get_document_url("get_document_text", document_id=document_id) + "?page=102",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'detail': "Page is out of range: from 1 to 100."}

    async def test_document_text_on_page_out_of_range_zero(self, client_user1: AsyncClient, documents_test_data):
        document_id = documents_test_data['_id']
        response = await client_user1.get(
            get_document_url("get_document_text", document_id=document_id) + "?page=0",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'detail': "Page is out of range: from 1 to 100."}

    async def test_document_text_on_page_out_of_range_negative(self, client_user1: AsyncClient, documents_test_data):
        document_id = documents_test_data['_id']
        response = await client_user1.get(
            get_document_url("get_document_text", document_id=document_id) + "?page=-2",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'detail': "Page is out of range: from 1 to 100."}

    async def test_document_voice_success(self, client_user1: AsyncClient, documents_test_data):
        document_id = documents_test_data['_id']
        response = await client_user1.get(
            get_document_url("get_document_voice", document_id=document_id) + "?page=2",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.content

    async def test_document_voice_failed(self, client_user1: AsyncClient, documents_test_data):
        document_id = documents_test_data['_id']
        response = await client_user1.get(
            get_document_url("get_document_voice", document_id=document_id) + "?page=-1",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'detail': "Page is out of range: from 1 to 100."}
