from decimal import Decimal
import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('documentary_audit',Path(__file__).parents[1]/'scripts/audit_city_hall_document.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def cells(unit='JOB',quantity='1',unit_cost='$900,000',total_cost='$900,000'):
    return dict(unit=unit,quantity=quantity,unit_cost=unit_cost,total_cost=total_cost)


def test_reference_zero_does_not_become_free_action():
    row=m.scalar_row(cells(unit='REF.',quantity='',unit_cost='$0',total_cost=''))
    assert row['accounting_role']=='reference_not_independent_action'
    assert row['source_unit_cost']=='0' and row['source_total_cost'] is None
    assert row['independent_action_cost'] is None


def test_costed_job_is_not_automatically_admitted_or_split():
    row=m.scalar_row(cells())
    assert row['source_total_cost']=='900000' and row['quantity_price_matches_total'] is True
    assert row['independent_action_cost'] is None


def test_exact_quantity_arithmetic_and_mismatch():
    assert m.scalar_row(cells(quantity='2.5',unit_cost='$0.10',total_cost='$0.25'))['quantity_price_matches_total'] is True
    assert m.scalar_row(cells(quantity='2',unit_cost='$100',total_cost='$150'))['quantity_price_matches_total'] is False


@pytest.mark.parametrize('value',['','$90,00','$900,00,0','REF.','900000USD'])
def test_unknown_money_is_not_silently_zero(value):
    assert m.number(value,money=True) is None


def test_valid_zero_stays_reported_value_without_admission():
    row=m.scalar_row(cells(unit_cost='$0',total_cost='$0'))
    assert row['quantity_price_matches_total'] is True and row['independent_action_cost'] is None
