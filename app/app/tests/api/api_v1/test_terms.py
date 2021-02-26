from random import choice, randint
from datetime import datetime, timedelta
from typing import Dict

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import crud
from app.core.config import settings
from app.models import Term
from app.schemas.users.admin import AdminPermissions
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.term import create_random_year, create_random_term
from app.tests.utils.utils import random_lower_string


def test_get_all_terms(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db=db)
    r = client.get(f"{settings.API_V1_STR}/terms/", headers=superuser_token_headers)
    assert 200 <= r.status_code < 300
    results = r.json()
    assert results
    assert results[0]['name'] == term.name
    assert results[0]['year_id'] == term.year_id
    assert results[0]['start_date'] == term.start_date
    assert results[0]['end_date'] == term.end_date


def test_get_term_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db=db)
    r = client.get(f"{settings.API_V1_STR}/terms/{term.id}", headers=superuser_token_headers)
    assert 200 <= r.status_code < 300
    fetched_term = r.json()
    assert fetched_term
    assert fetched_term['id'] == term.id
    assert fetched_term['start_date'] == term.start_date
    assert fetched_term['end_date'] == term.end_date
    assert fetched_term['is_active'] and term.is_active


def test_get_term_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    last_term_id = db.query(Term).order_by(Term.id.desc()).first().id
    r = client.get(f"{settings.API_V1_STR}/terms/{last_term_id+1}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_create_term(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    name = random_lower_string()
    year_id = create_random_year(db=db).id
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=90)
    current_year_term = randint(1, 4)
    has_electives = choice([True, False])
    data = {
        'name': name,
        'year_id': year_id,
        'start_date': start_date,
        'end_date': end_date,
        'current_year_term': current_year_term,
        'has_electives': has_electives,
    }
    r = client.post(f"{settings.API_V1_STR}/terms/", headers=superuser_token_headers, json=data)
    assert 200 <= r.status_code < 300
    created_term = r.json()
    fetched_term = crud.term.get_by_details(
        db=db,
        name=name,
        year_id=year_id,
        current_year_term=current_year_term,
        start_date=start_date,
        end_date=end_date,
    )
    assert fetched_term
    assert created_term['name'] == fetched_term.name == name
    assert created_term['year_id'] == fetched_term.year_id == year_id
    assert created_term['start_date'] == fetched_term.start_date == start_date
    assert created_term['end_date'] == fetched_term.end_date == end_date
    assert created_term['current_year_term'] == fetched_term.current_year_term == current_year_term
    assert created_term['has_electives'] and fetched_term.has_electives
    assert created_term['is_active'] and fetched_term.is_active


def test_create_term_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db=db)
    data = {
        'name': term.name,
        'year_id': term.year_id,
        'start_date': term.start_date,
        'end_date': term.end_date,
        'current_year_term': term.current_year_term,
    }
    r = client.post(f"{settings.API_V1_STR}/terms/", headers=superuser_token_headers, json=data)
    assert r.status_code == 409


def test_get_term_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(f"{settings.API_V1_STR}/terms/", headers=normal_user_token_headers)
    assert r.status_code == 403


def test_update_term_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    last_term_id = db.query(Term).order_by(Term.id.desc()).first().id
    r = client.put(f"{settings.API_V1_STR}/terms/{last_term_id + 1}", headers=superuser_token_headers, json={})
    assert r.status_code == 404


def test_update_term(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db=db)
    assert term.start_date
    assert term.end_date
    data = {
        'start_date': term.start_date - timedelta(days=6 * 30),
        'end_date': term.end_date - timedelta(days=6 * 30),
        'is_active': not term.is_active,
    }
    r = client.put(f"{settings.API_V1_STR}/terms/{term.id}", headers=superuser_token_headers, json=data)
    fetched_term = r.json()
    assert fetched_term
    assert fetched_term['id'] == term.id
    assert fetched_term['start_date'] == term.start_date - timedelta(days=6 * 30)
    assert fetched_term['end_date'] == term.end_date - timedelta(days=6 * 30)
    assert fetched_term['is_active'] != term.is_active


def test_get_term_admin(client: TestClient, db: Session) -> None:
    admin_perms = AdminPermissions(0)
    admin_perms['term'] = True
    admin = create_random_user(db=db, type="admin", permissions=admin_perms.permissions)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type='admin'
    )
    r = client.get(f"{settings.API_V1_STR}/terms/", headers=admin_user_token_headers)
    assert r.status_code == 200


def test_get_term_weakadmin(client: TestClient, db: Session) -> None:
    admin = create_random_user(db=db, type="admin", permissions=0)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type='admin'
    )
    r = client.get(f"{settings.API_V1_STR}/terms/", headers=admin_user_token_headers)
    assert r.status_code == 403


def test_delete_term(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db=db)
    r = client.delete(f"{settings.API_V1_STR}/terms/{term.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    deleted_term = crud.term.get(db=db, id=term.id)
    assert deleted_term is None


def test_delete_term_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    last_term_id = db.query(Term).order_by(Term.id.desc()).first().id
    r = client.delete(f"{settings.API_V1_STR}/terms/{last_term_id+1}", headers=superuser_token_headers)
    assert r.status_code == 404