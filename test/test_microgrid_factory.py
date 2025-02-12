from mgts.microgrid import MicrogridFactory

def test_create():
    path = "./datasets/test.xlsx"
    sheet_name="MG1"

    mgf = MicrogridFactory(path=path)

    microgrid = mgf.create_from_sheet(sheet_name=sheet_name)

    assert microgrid.consumed_energy==[0, 5, 15, 15, 15, 15, 15, 15, 15]
    assert microgrid.produced_energy==[0, 10, 15, 20, 25, 25, 25, 25, 25]

    sheet_name="MG2"

    microgrid = mgf.create_from_sheet(sheet_name=sheet_name)

    assert microgrid.consumed_energy==[0, 5, 15, 15, 15, 15, 8, 7, 6]
    assert microgrid.produced_energy==[0, 10, 15, 20, 25, 25, 20, 20, 20]