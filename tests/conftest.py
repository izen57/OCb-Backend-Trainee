# Взял код с https://docs.pytest.org/en/stable/example/simple.html#incremental-testing-test-steps.
import pytest
from sqlmodel import SQLModel, Session, StaticPool, create_engine

from main import app


# История провалов тестов по каждому классу и индексу параметризации.
_test_failed_incremental: dict[str, dict[tuple[int, ...], str]] = {}

def pytest_runtest_makereport(item, call):
    if item.get_closest_marker('incremental'):
        # incremental marker is used
        if call.excinfo is not None:
            # the test has failed
            # retrieve the class name of the test
            cls_name = str(item.cls)
            # retrieve the index of the test (if parametrize is used in combination with incremental)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, 'callspec')
                else ()
            )
            # retrieve the name of the test function
            test_name = item.originalname or item.name
            # store in _test_failed_incremental the original name of the failed test
            _test_failed_incremental.setdefault(cls_name, {}).setdefault(
                parametrize_index, test_name
            )

def pytest_runtest_setup(item):
    if item.get_closest_marker('incremental'):
        # retrieve the class name of the test
        cls_name = str(item.cls)
        # check if a previous test has failed for this class
        if cls_name in _test_failed_incremental:
            # retrieve the index of the test (if parametrize is used in combination with incremental)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, 'callspec')
                else ()
            )
            # retrieve the name of the first test function to fail for this class name and index
            test_name = _test_failed_incremental[cls_name].get(parametrize_index, None)
            # if name found, test has failed for the combination of class name & test name
            if test_name is not None:
                pytest.skip(f'Предыдущий тест {test_name} провалился.')

def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'incremental: mark test to run only on named environment'
    )

# @pytest.fixture(name='session')  
# def session_fixture():  
#     engine = create_engine(
#         'sqlite://',
#         connect_args={'check_same_thread': False},
#         poolclass=StaticPool
#     )
#     SQLModel.metadata.create_all(engine)
#     with Session(engine) as session:
#         yield session

# @pytest.fixture(name='client')  
# def client_fixture(session: Session):  
#     def get_session_override():  
#         return session

#     app.dependency_overrides[get_session] = get_session_override  

#     client = TestClient(app)  
#     yield client  
#     app.dependency_overrides.clear()