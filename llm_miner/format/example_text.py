chemical_formula="""
Paragraph: The LiFePO4 cathode material exhibits excellent electrochemical performance with a capacity of 170 mAh/g. LiCoO2 is another common cathode material used in lithium-ion batteries.
JSON: ```JSON
[{{"value":"LiFePO4", "condition":""}}, {{"value":"LiCoO2", "condition":""}}]
```
"""

capacity="""
Paragraph: The LiFePO4 cathode material delivers a high specific capacity of 170 mAh/g, while the LiCoO2 cathode achieves 150 mAh/g under standard conditions. The theoretical capacity of LiFePO4 is 178 mAh/g.
JSON: ```JSON
[{{"value":"170", "unit":"mAh/g", "type":"specific", "condition":""}}, {{"value":"150", "unit":"mAh/g", "type":"specific", "condition":""}}, {{"value":"178", "unit":"mAh/g", "type":"theoretical", "condition":""}}]
```
"""

energy_density="""
Paragraph: The lithium-ion battery with LiFePO4 cathode demonstrates a gravimetric energy density of 586 Wh/kg and a volumetric energy density of 1280 Wh/L.
JSON: ```JSON
[{{"value":"586", "unit":"Wh/kg", "type":"gravimetric", "condition":""}}, {{"value":"1280", "unit":"Wh/L", "type":"volumetric", "condition":""}}]
```
"""

power_density="""
Paragraph: The battery system achieves a specific power density of 5000 W/kg, enabling fast charging capabilities.
JSON: ```JSON
[{{"value":"5000", "unit":"W/kg", "type":"specific", "condition":""}}]
```
"""

voltage="""
Paragraph: The operating voltage of the LiFePO4 battery is approximately 3.4 V, while the LiCoO2 battery operates at 3.7 V.
JSON: ```JSON
[{{"value":"3.4", "unit":"V", "type":"operating", "condition":""}}, {{"value":"3.7", "unit":"V", "type":"operating", "condition":""}}]
```
"""

coulombic_efficiency="""
Paragraph: The battery exhibits excellent coulombic efficiency of 98% over 500 charge-discharge cycles, indicating minimal capacity loss.
JSON: ```JSON
[{{"value":"98", "unit":"%", "type":"charge", "condition":""}}]
```
"""

cycle_life="""
Paragraph: The Li-ion battery maintains 80% of its initial capacity after 1000 cycles, demonstrating excellent cycle stability.
JSON: ```JSON
[{{"value":"1000", "unit":"cycles", "condition":""}}]
```
"""

electrode_thickness="""
Paragraph: The cathode electrode has a thickness of 50 μm, while the anode electrode is 40 μm thick.
JSON: ```JSON
[{{"value":"50", "unit":"μm", "type":"cathode", "condition":""}}, {{"value":"40", "unit":"μm", "type":"anode", "condition":""}}]
```
"""

particle_size="""
Paragraph: The active material particles have an average diameter of 100 nm, which contributes to improved electrochemical performance.
JSON: ```JSON
[{{"value":"100", "unit":"nm", "type":"diameter", "condition":""}}]
```
"""

ionic_conductivity="""
Paragraph: The ionic conductivity of the solid electrolyte is 1.2 × 10^-3 S/cm at room temperature, facilitating efficient Li+ ion transport.
JSON: ```JSON
[{{"value":"1.2 × 10^-3", "unit":"S/cm", "type":"Li+", "condition":"room temperature"}}]
```
"""

electronic_conductivity="""
Paragraph: The electronic conductivity of the cathode material is measured at 0.5 S/cm, ensuring good electrical pathways within the electrode.
JSON: ```JSON
[{{"value":"0.5", "unit":"S/cm", "condition":""}}]
```
"""

diffusivity="""
Paragraph: The diffusivity of Li+ ions in the electrode material is 2.5 × 10^-10 cm²/s, which affects the rate capability of the battery.
JSON: ```JSON
[{{"value":"2.5 × 10^-10", "unit":"cm²/s", "type":"Li+", "condition":""}}]
```
"""

young_modulus="""
Paragraph: The Young's modulus of the electrode material is 120 GPa, indicating its mechanical stiffness and resistance to deformation.
JSON: ```JSON
[{{"value":"120", "unit":"GPa", "condition":""}}]
```
"""

volume_expansion="""
Paragraph: The battery electrode experiences a volume expansion of 10% during the lithiation process, which can lead to capacity fading over time.
JSON: ```JSON
[{{"value":"10", "unit":"%", "condition":"lithiation"}}]
```
"""

activation_energy="""
Paragraph: The activation energy for Li+ ion diffusion in the solid electrolyte is 0.5 eV, determined from Arrhenius analysis over a temperature range of 25-100°C.
JSON: ```JSON
[{{"value":"0.5", "unit":"eV", "type":"diffusion", "condition":"25-100°C"}}]
```
"""

band_gap="""
Paragraph: The semiconductor material exhibits a direct band gap of 1.5 eV, which is suitable for photovoltaic applications.
JSON: ```JSON
[{{"value":"1.5", "unit":"eV", "type":"direct", "condition":""}}]
```
"""

current_density="""
Paragraph: The electrode achieves a current density of 2 mA/cm² during the discharge process at a voltage of 3.5 V.
JSON: ```JSON
[{{"value":"2", "unit":"mA/cm²", "type":"discharge", "condition":"3.5 V"}}]
```
"""


