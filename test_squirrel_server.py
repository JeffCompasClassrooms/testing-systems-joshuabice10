import os
import shutil
import subprocess
import time
import pytest
import http.client
import json
import sqlite3

SERVER_PY = "squirrel_server.py"
REAL_DB = "squirrel_db.db"
EMPTY_DB = "empty_squirrel_db.db"
BASE_HOST = "127.0.0.1"
BASE_PORT = 8080

def kill_existing_squirrel_servers():
        subprocess.run(
            ["pkill", "-f", SERVER_PY],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(0.5)


@pytest.fixture(autouse=True)
def run_server_with_test_db():
    kill_existing_squirrel_servers()

    backup_db = None
    if os.path.exists(REAL_DB):
        backup_db = REAL_DB + ".backup"
        os.rename(REAL_DB, backup_db)
    shutil.copy(EMPTY_DB, REAL_DB)

    process = subprocess.Popen(["python3", SERVER_PY])
    time.sleep(0.5)

    try:
        yield
    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()

        if os.path.exists(REAL_DB):
            os.remove(REAL_DB)
        if backup_db and os.path.exists(backup_db):
            os.rename(backup_db, REAL_DB)

def insert_squirrel(name, size):
    connection = sqlite3.connect("squirrel_db.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO squirrels (name, size) VALUES (?, ?)", (name, size))
    connection.commit()
    connection.close()

def describe_Testing_Squirrel_Server_DB():

    def describe_handleSquirrelsIndex_Method():

        def it_returns_the_correct_status_code_when_db_is_empty():
            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
            connection.request("GET", "/squirrels")
            response = connection.getresponse()
            
            assert response.status == 200
            connection.close()
        
        def it_returns_the_correct_header_when_db_is_empty():
            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
            connection.request("GET", "/squirrels")
            response = connection.getresponse()
            
            assert response.getheader("Content-Type") == "application/json"
            connection.close()

        def it_returns_empty_list_when_db_is_empty():
            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
            connection.request("GET", "/squirrels")
            response = connection.getresponse()
            
            data = json.loads(response.read())
            assert data == []
            connection.close()

        def it_returns_the_correct_status_code_when_db_has_some_squirrels():
            insert_squirrel("Tiny", "big")
            insert_squirrel("Humungo", "small")

            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
            connection.request("GET", "/squirrels")
            response = connection.getresponse()
            
            assert response.status == 200
            connection.close()

        def it_returns_the_correct_header_when_db_has_come_squirrels():
            insert_squirrel("Tiny", "big")
            insert_squirrel("Humungo", "small")

            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
            connection.request("GET", "/squirrels")
            response = connection.getresponse()

            assert response.getheader("Content-Type") == "application/json"
            connection.close()

        def it_returns_all_squirrels_when_db_has_some_squirrels():
            insert_squirrel("Tiny", "big")
            insert_squirrel("Humungo", "small")

            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
            connection.request("GET", "/squirrels")
            response = connection.getresponse()

            data = json.loads(response.read())
            assert data == [
                {'id': 1, 'name': 'Tiny', 'size': 'big'},
                {'id': 2, 'name': 'Humungo', 'size': 'small'}
            ]
            connection.close()
    
    def describe_handleSquirrelsRetrieve_Method():

        def describe_Successes():
            def it_returns_the_correct_status_code_when_retrieving_a_squirrel():
                insert_squirrel("Humungo", "small")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
                connection.request("GET", "/squirrels/1")
                response = connection.getresponse()

                assert response.status == 200
                connection.close()

            def it_returns_the_correct_header_when_retrieving_a_squirrel():
                insert_squirrel("Humungo", "small")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
                connection.request("GET", "/squirrels/1")
                response = connection.getresponse()

                assert response.getheader("Content-Type") == "application/json"
                connection.close()

            def it_returns_the_squirrel_correctly_when_only_one_exists():
                insert_squirrel("Humungo", "small")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
                connection.request("GET", "/squirrels/1")
                response = connection.getresponse()

                data = json.loads(response.read())
                assert data == {'id': 1, 'name': 'Humungo', 'size': 'small'}
                connection.close()

            def it_returns_the_squirrel_correctly_when_many_exist():
                insert_squirrel("Pig", "big")
                insert_squirrel("Chicken", "medium")
                insert_squirrel("Hoppy", "Huge")
                insert_squirrel("Humungo", "small")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
                connection.request("GET", "/squirrels/4")
                response = connection.getresponse()

                data = json.loads(response.read())
                assert data == {'id': 4, 'name': 'Humungo', 'size': 'small'}
                connection.close()

        def describe_Fails():
            def it_returns_404_when_retrieving_a_squirrel_from_an_empty_db():
                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
                connection.request("GET", "/squirrels/1")
                response = connection.getresponse()

                assert response.status == 404
                connection.close()

            def it_returns_404_when_retrieving_a_squirrel_that_does_not_exist():
                insert_squirrel("Pig", "big")
                insert_squirrel("Chicken", "medium")
                insert_squirrel("Hoppy", "Huge")
                insert_squirrel("Humungo", "small")
                
                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
                connection.request("GET", "/squirrels/5")
                response = connection.getresponse()

                assert response.status == 404
                connection.close()

    def describe_handleSquirrelsCreate_Method():

        def it_returns_the_correct_status_code_when_creating_a_squirrel():
            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

            created_body = "name=Humungo&size=small"
            created_headers = {"Content-Type": "application/x-www-form-urlencoded"}

            connection.request("POST", "/squirrels", body=created_body, headers=created_headers)
            response = connection.getresponse()

            assert response.status == 201
            response.read()
            connection.close()

        def it_returns_the_correct_status_code_when_creating_multiple_squirrels():
            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

            created_body = "name=Humungo&size=small"
            created_headers = {"Content-Type": "application/x-www-form-urlencoded"}

            connection.request("POST", "/squirrels", body=created_body, headers=created_headers)
            response = connection.getresponse()

            assert response.status == 201
            response.read()

            created_body2 = "name=Hoppy&size=huge"
            created_headers2 = {"Content-Type": "application/x-www-form-urlencoded"}

            connection.request("POST", "/squirrels", body=created_body2, headers=created_headers2)
            response2 = connection.getresponse()

            assert response.status == 201
            response.read()
            connection.close()


        def it_creates_one_squirrel_correctly():
            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

            created_body = "name=Humungo&size=small"
            created_headers = {"Content-Type": "application/x-www-form-urlencoded"}

            connection.request("POST", "/squirrels", body=created_body, headers=created_headers)
            response = connection.getresponse()
            response.read()

            connection.request("GET", "/squirrels/1")
            response = connection.getresponse()
            data = json.loads(response.read())
            assert data == {'id': 1, 'name': 'Humungo', 'size': 'small'}
            connection.close()

        def it_creates_multiple_squirrels_correctly():
            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

            created_body = "name=Humungo&size=small"
            created_headers = {"Content-Type": "application/x-www-form-urlencoded"}

            connection.request("POST", "/squirrels", body=created_body, headers=created_headers)
            response = connection.getresponse()
            response.read()

            created_body2 = "name=Hoppy&size=big"
            created_headers2 = {"Content-Type": "application/x-www-form-urlencoded"}

            connection.request("POST", "/squirrels", body=created_body2, headers=created_headers2)
            response = connection.getresponse()
            response.read()

            connection.request("GET", "/squirrels/1")
            response = connection.getresponse()
            data = json.loads(response.read())
            assert data == {'id': 1, 'name': 'Humungo', 'size': 'small'}

            connection.request("GET", "/squirrels/2")
            response = connection.getresponse()
            data = json.loads(response.read())
            assert data == {'id': 2, 'name': 'Hoppy', 'size': 'big'}
            
            connection.close()
        
        def it_returns_400_on_bad_request():
            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

            body = "name=HalfSquirrel"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            connection.request("POST", "/squirrels", body=body, headers=headers)
            response = connection.getresponse()

            assert response.status == 400
            connection.close()

    def describe_handleSquirrelsUpdate_Method():

        
        def describe_Successes():
            def it_sends_the_correct_status_code_when_updating_a_squirrel():
                insert_squirrel("Humungo", "small")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                updated_body = "name=Humungus&size=huge"
                updated_headers = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/1", body=updated_body, headers=updated_headers)
                response = connection.getresponse()

                assert response.status == 204
                response.read()
                connection.close()

            def it_sends_the_correct_status_code_when_updating_multiple_squirrels():
                insert_squirrel("Humungo", "small")
                insert_squirrel("Hoppy", "big")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                updated_body = "name=Humungus&size=huge"
                updated_headers = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/1", body=updated_body, headers=updated_headers)
                response = connection.getresponse()

                assert response.status == 204
                response.read()

                updated_body2 = "name=Jumpy&size=medium"
                updated_headers2 = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/2", body=updated_body2, headers=updated_headers2)
                response = connection.getresponse()

                assert response.status == 204
                response.read()
                connection.close()

            def it_sends_the_correct_status_code_when_updating_the_same_squirrel_multiple_times():
                insert_squirrel("Humungo", "small")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                updated_body = "name=Humungus&size=huge"
                updated_headers = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/1", body=updated_body, headers=updated_headers)
                response = connection.getresponse()

                assert response.status == 204
                response.read()

                updated_body2 = "name=Enormo&size=massive"
                updated_headers2 = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/1", body=updated_body, headers=updated_headers)
                response = connection.getresponse()

                assert response.status == 204
                response.read()

                connection.close()

            def it_updates_a_squirrel_correctly():
                insert_squirrel("Humungo", "small")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                updated_body = "name=Humungus&size=huge"
                updated_headers = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/1", body=updated_body, headers=updated_headers)
                response = connection.getresponse()
                response.read()

                connection.request("GET", "/squirrels/1")
                response = connection.getresponse()
                data = json.loads(response.read())
                assert data == {"id": 1, "name": "Humungus", "size": "huge"}
                connection.close()

            def it_updates_multiple_squirrels_correctly():
                insert_squirrel("Humungo", "small")
                insert_squirrel("Hoppy", "big")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                updated_body = "name=Humungus&size=huge"
                updated_headers = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/1", body=updated_body, headers=updated_headers)
                response = connection.getresponse()
                response.read()

                updated_body2 = "name=Jumpy&size=medium"
                updated_headers2 = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/2", body=updated_body2, headers=updated_headers2)
                response = connection.getresponse()
                response.read()

                connection.request("GET", "/squirrels/1")
                response = connection.getresponse()
                data = json.loads(response.read())
                assert data == {"id": 1, "name": "Humungus", "size": "huge"}

                connection.request("GET", "/squirrels/2")
                response = connection.getresponse()
                data = json.loads(response.read())
                assert data == {"id": 2, "name": "Jumpy", "size": "medium"}

                connection.close()

            def it_updates_a_squirrel_multiple_times_correctly():
                insert_squirrel("Humungo", "small")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                updated_body = "name=Humungus&size=huge"
                updated_headers = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/1", body=updated_body, headers=updated_headers)
                response = connection.getresponse()
                response.read()

                connection.request("GET", "/squirrels/1")
                response = connection.getresponse()
                data = json.loads(response.read())
                assert data == {"id": 1, "name": "Humungus", "size": "huge"}

                updated_body2 = "name=Enormo&size=massive"
                updated_headers2 = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/1", body=updated_body2, headers=updated_headers2)
                response = connection.getresponse()
                response.read()

                connection.request("GET", "/squirrels/1")
                response = connection.getresponse()
                data = json.loads(response.read())
                assert data == {"id": 1, "name": "Enormo", "size": "massive"}

                connection.close()
        
        def describe_Fails():

            def it_returns_404_when_trying_to_update_a_nonexistent_squirrel():
                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                body = "name=Ghost&size=huge"
                headers = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/1", body=body, headers=headers)
                response = connection.getresponse()

                assert response.status == 404
                connection.close()

            def it_returns_correct_body_when_trying_to_update_a_nonexistent_squirrel():
                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                body = "name=Ghost&size=huge"
                headers = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/1", body=body, headers=headers)
                response = connection.getresponse()

                body_text = response.read().decode("utf-8")
                assert body_text == "404 Not Found"
                connection.close()

            def it_returns_404_when_trying_to_update_a_nonexistent_squirrel_when_multiple_squirrels_exist():
                insert_squirrel("Humungo", "small")
                insert_squirrel("Hoppy", "big")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                body = "name=Ghost&size=huge"
                headers = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/3", body=body, headers=headers)
                response = connection.getresponse()

                assert response.status == 404
                connection.close()

            def it_returns_correct_body_when_trying_to_update_a_nonexistent_squirrel_when_multiple_squirrels_exist():
                insert_squirrel("Humungo", "small")
                insert_squirrel("Hoppy", "big")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                body = "name=Ghost&size=huge"
                headers = {"Content-Type": "application/x-www-form-urlencoded"}

                connection.request("PUT", "/squirrels/3", body=body, headers=headers)
                response = connection.getresponse()

                body_text = response.read().decode("utf-8")
                assert body_text == "404 Not Found"
                connection.close()

    def describe_handleSquirrelsDelete_Method():

        def describe_Successes():

            def it_returns_status_code_correctly_when_deleting_a_squirrel():
                insert_squirrel("Humungo", "small")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                connection.request("DELETE", "/squirrels/1")
                response = connection.getresponse()

                assert response.status == 204
                response.read()
                connection.close()

            def it_deletes_a_squirrel_correctly():
                insert_squirrel("Humungo", "small")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                connection.request("DELETE", "/squirrels/1")
                response = connection.getresponse()
                response.read()

                connection.request("GET", "/squirrels/1")
                response = connection.getresponse()
                assert response.status == 404
                body_text = response.read().decode("utf-8")
                assert body_text == "404 Not Found"
                connection.close()

            def it_deletes_the_correct_squirrel_when_there_are_many():
                insert_squirrel("Enormo", "massive")
                insert_squirrel("Humungo", "small")
                insert_squirrel("Hoppy", "huge")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                connection.request("DELETE", "/squirrels/2")
                response = connection.getresponse()
                response.read()

                connection.request("GET", "/squirrels/2")
                response = connection.getresponse()
                assert response.status == 404
                body_text = response.read().decode("utf-8")
                assert body_text == "404 Not Found"
                connection.close()

            def it_deletes_multiple_squirrels_correctly():
                insert_squirrel("Enormo", "massive")
                insert_squirrel("Humungo", "small")
                insert_squirrel("Hoppy", "huge")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                connection.request("DELETE", "/squirrels/1")
                response = connection.getresponse()
                response.read()

                connection.request("DELETE", "/squirrels/2")
                response = connection.getresponse()
                response.read()

                connection.request("GET", "/squirrels/1")
                response = connection.getresponse()
                assert response.status == 404
                body_text = response.read().decode("utf-8")
                assert body_text == "404 Not Found"

                connection.request("GET", "/squirrels/2")
                response = connection.getresponse()
                assert response.status == 404
                body_text = response.read().decode("utf-8")
                assert body_text == "404 Not Found"
                connection.close()

            def it_does_not_do_anything_to_a_different_squirrel_when_deleting():
                insert_squirrel("Enormo", "massive")
                insert_squirrel("Humungo", "small")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                connection.request("DELETE", "/squirrels/1")
                response = connection.getresponse()
                response.read()

                connection.request("GET", "/squirrels/1")
                response = connection.getresponse()
                assert response.status == 404
                body_text = response.read().decode("utf-8")
                assert body_text == "404 Not Found"

                connection.request("GET", "/squirrels/2")
                response = connection.getresponse()
                data = json.loads(response.read())
                assert data == {"id": 2, "name": "Humungo", "size": "small"}
                connection.close()
        
        def describe_Fails():

            def it_returns_404_when_trying_to_delete_with_empty_db():
                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                connection.request("DELETE", "/squirrels/1")
                response = connection.getresponse()
                assert response.status == 404
                response.read()
                connection.close()

            def it_returns_correct_body_when_trying_to_delete_with_empty_db():
                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                connection.request("DELETE", "/squirrels/1")
                response = connection.getresponse()
                body_text = response.read().decode("utf-8")
                assert body_text == "404 Not Found"
                connection.close()

            def it_returns_404_when_trying_to_delete_bad_squirrel_when_squirrels_exist():
                insert_squirrel("Enormo", "massive")
                insert_squirrel("Humungo", "small")
                insert_squirrel("Hoppy", "huge")
                
                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                connection.request("DELETE", "/squirrels/4")
                response = connection.getresponse()
                assert response.status == 404
                response.read()
                connection.close()

            def it_returns_correct_body_when_trying_to_delete_bad_squirrel_when_squirrels_exist():
                insert_squirrel("Enormo", "massive")
                insert_squirrel("Humungo", "small")
                insert_squirrel("Hoppy", "huge")
                
                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

                connection.request("DELETE", "/squirrels/4")
                response = connection.getresponse()
                body_text = response.read().decode("utf-8")
                assert body_text == "404 Not Found"
                connection.close()

            def it_returns_404_when_trying_to_delete_already_deleted_squirrel():
                insert_squirrel("Enormo", "massive")
                insert_squirrel("Humungo", "small")
                insert_squirrel("Hoppy", "huge")

                connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
                connection.request("DELETE", "/squirrels/2")
                response = connection.getresponse()
                response.read()

                connection.request("DELETE", "/squirrels/2")
                response = connection.getresponse()
                assert response.status == 404
                body_text = response.read().decode("utf-8")
                assert body_text == "404 Not Found"
                connection.close()
        
    def describe_handle404():

        def it_returns_404_for_invalid_path(run_server_with_test_db):
            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

            connection.request("GET", "/not_a_squirrel")
            response = connection.getresponse()
            assert response.status == 404
            assert response.getheader("Content-Type") == "text/plain"
            body = response.read().decode("utf-8")
            assert body == "404 Not Found"
            connection.close()

        def it_returns_404_for_wrong_method(run_server_with_test_db):
            connection = http.client.HTTPConnection(BASE_HOST, BASE_PORT)

            connection.request("POST", "/squirrels/1", body="name=Ghost&size=huge",
                        headers={"Content-Type": "application/x-www-form-urlencoded"})
            response = connection.getresponse()
            assert response.status == 404
            body = response.read().decode("utf-8")
            assert body == "404 Not Found"
            connection.close()




