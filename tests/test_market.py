from energy_storage_dispatch_model_interview.market import EnergyMarket

def test_hourly_price_imports():
    expected_answer = [51.89, 55.49, 51.06, 44.76, 40.07]
    hourly_market = EnergyMarket
    hourly_market.read_price_file("market_data_Hourly data.csv")

    np.testing.assert_allclose(hourly_market._price[:5], expected_answer)
