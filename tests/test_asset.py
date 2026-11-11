from energy_storage_dispatch_model_interview.asset import Asset


def test_a_valid_asset_keeps_its_values_and_efficiencies_default_to_lossless():
    """An asset holds exactly the limits it is given (distinct values, so swapped fields would
    show), and with no efficiencies given it is lossless (1.0 in both directions)."""
    asset = Asset(max_charge_power=2.0, max_discharge_power=1.5, energy_capacity=4.0)

    assert asset.max_charge_power == 2.0
    assert asset.max_discharge_power == 1.5
    assert asset.energy_capacity == 4.0
    assert asset.charge_efficiency == 1.0
    assert asset.discharge_efficiency == 1.0

    lossy = Asset(
        max_charge_power=2.0,
        max_discharge_power=1.5,
        energy_capacity=4.0,
        charge_efficiency=0.95,
        discharge_efficiency=0.9,
    )

    assert lossy.charge_efficiency == 0.95
    assert lossy.discharge_efficiency == 0.9
