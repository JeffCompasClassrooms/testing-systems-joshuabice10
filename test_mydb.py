import os
import shutil
from mydb import MyDB
import pytest
import pickle

@pytest.fixture(autouse=True)
def setup_and_teardown():
    if os.path.exists("test_copy_db.db"):
        print("It's already there!")
    else:
        with open("test_copy_db.db", "a"):
            pass
    yield
    os.remove("test_copy_db.db")



def describe_Testing_MyDB_Class():
    
    def describe_init_of_MyDB_():
        
        def it_creates_file_if_given_file_which_does_not_exist():
            db = MyDB("testing_a_db.db")
            assert os.path.exists("testing_a_db.db")
            if os.path.exists("testing_a_db.db"):
                os.remove("testing_a_db.db")

        def it_assigns_correct_file_to_fname_if_file_exists():
            db = MyDB("test_copy_db.db")
            
            assert os.path.exists("test_copy_db.db")
            assert db.fname == "test_copy_db.db"

    def describe_loadStrings_Method():

        def it_loads_the_correct_information_from_the_file_when_it_is_empty():
            with open("test_copy_db.db", "wb") as f:
                pickle.dump([], f)
            
            db = MyDB("test_copy_db.db")
            
            assert db.loadStrings() == []

        def it_loads_the_correct_information_from_the_file_with_one_object():
            with open("test_copy_db.db", "wb") as f:
                pickle.dump([{"name": "Test"}], f)
            
            db = MyDB("test_copy_db.db")
            
            assert db.loadStrings() == [{"name": "Test"}]
        
        def it_loads_the_correct_information_from_the_file_with_many_objects():
            with open("test_copy_db.db", "wb") as f:
                pickle.dump([{"name": "Test"}, {"name": "Test2"}, {"name": "Test3"}, {"name": "Test4"}], f)
            
            db = MyDB("test_copy_db.db")
            
            assert db.loadStrings() == [{"name": "Test"}, {"name": "Test2"}, {"name": "Test3"}, {"name": "Test4"}]

    def describe_saveStrings_Method():

        def it_saves_an_empty_array_correctly():
            db = MyDB("test_copy_db.db")

            db.saveStrings([])

            data = None
            with open("test_copy_db.db", "rb") as f:
                data = pickle.load(f)
            assert data == []
        
        def it_saves_an_array_with_one_object_correctly():
            db = MyDB("test_copy_db.db")

            db.saveStrings([{"name": "Test"}])

            data = None
            with open("test_copy_db.db", "rb") as f:
                data = pickle.load(f)
            assert data == [{"name": "Test"}]

        def it_saves_an_array_with_many_objects_correctly():
            db = MyDB("test_copy_db.db")

            db.saveStrings([{"name": "Test"}, {"name": "Test2"}, {"name": "Test3"}, {"name": "Test4"}])

            data = None
            with open("test_copy_db.db", "rb") as f:
                data = pickle.load(f)
            assert data == [{"name": "Test"}, {"name": "Test2"}, {"name": "Test3"}, {"name": "Test4"}]

        def it_creates_a_new_file_if_given_one_that_does_not_exist_and_saves_data():
            db = MyDB("testing_saveStrings_creation.db")
            data = None
            with open("testing_saveStrings_creation.db", "rb") as f:
                data = pickle.load(f)

            assert os.path.exists("testing_saveStrings_creation.db")
            assert data == []
            
            db.saveStrings([{"name": "Test"}, {"name": "Test2"}, {"name": "Test3"}, {"name": "Test4"}])
            with open("testing_saveStrings_creation.db", "rb") as f:
                data = pickle.load(f)

            assert data == [{"name": "Test"}, {"name": "Test2"}, {"name": "Test3"}, {"name": "Test4"}]

            if os.path.exists("testing_saveStrings_creation.db"):
                os.remove("testing_saveStrings_creation.db")
    
    def describe_saveString_Method():

        def it_saves_an_empty_string_to_an_empty_array():
            with open("test_copy_db.db", "wb") as f:
                pickle.dump([], f)
            db = MyDB("test_copy_db.db")

            db.saveString("")

            data = None
            with open("test_copy_db.db", "rb") as f:
                data = pickle.load(f)

            assert data == [""]

        def it_saves_a_string_to_an_empty_array():
            with open("test_copy_db.db", "wb") as f:
                pickle.dump([], f)
            db = MyDB("test_copy_db.db")

            db.saveString("Earthbender")

            data = None
            with open("test_copy_db.db", "rb") as f:
                data = pickle.load(f)

            assert data == ["Earthbender"]

        def it_saves_an_empty_string_to_an_array_that_has_another_item():
            with open("test_copy_db.db", "wb") as f:
                pickle.dump([{"name": "Test"}], f)
            db = MyDB("test_copy_db.db")

            db.saveString("")

            data = None
            with open("test_copy_db.db", "rb") as f:
                data = pickle.load(f)

            assert data == [{"name": "Test"}, ""]

        def it_saves_a_string_with_characters_to_an_array_that_has_another_item():
            with open("test_copy_db.db", "wb") as f:
                pickle.dump([{"name": "Test"}], f)
            db = MyDB("test_copy_db.db")

            db.saveString("!Earthbender1")

            data = None
            with open("test_copy_db.db", "rb") as f:
                data = pickle.load(f)

            assert data == [{"name": "Test"}, "!Earthbender1"]

        def it_saves_multiple_strings_with_characters_to_an_array_that_has_another_item():
            with open("test_copy_db.db", "wb") as f:
                pickle.dump([{"name": "Test"}], f)
            db = MyDB("test_copy_db.db")

            db.saveString("!Earthbender1")
            db.saveString("@Waterbender2")

            data = None
            with open("test_copy_db.db", "rb") as f:
                data = pickle.load(f)

            assert data == [{"name": "Test"}, "!Earthbender1", "@Waterbender2"]