from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_semantic_controls import control
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.oracle import exact_oracle


def test_controls_expose_physical_and_cost_semantics():
    cases=authored_interface_scenarios()
    instance=cases['shared_asset'];oracle=exact_oracle(instance)
    graph=control(instance,oracle,'graph-only')
    assert (graph['original_cost'],graph['strict_cost'],graph['full_model_valid'])==('2','5',False)
    reuse=control(instance,oracle,'no-owner-reuse')
    assert (reuse['original_cost'],reuse['strict_cost'],reuse['full_model_valid'])==('10','5',True)
    instance=cases['atomic_bundle'];oracle=exact_oracle(instance)
    price=control(instance,oracle,'per-effect-price')
    assert (price['original_cost'],price['strict_cost'],price['selected'])==('4','3',['A002','A003'])
    instance=cases['unused_paid_geometry'];oracle=exact_oracle(instance)
    graph=control(instance,oracle,'graph-only')
    assert (graph['original_cost'],graph['strict_cost'],graph['full_model_valid'])==('2','6',False)
