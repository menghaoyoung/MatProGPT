import inspect
from typing import Dict, Iterable
from collections.abc import Mapping
from llm_miner.format import structured_data as st_data
from llm_miner.format import explanation as explain_data
from llm_miner.format import information as info_data
from llm_miner.format import example_table
from llm_miner.format import example_text
from llm_miner.format import operation


class BaseFormatter(Mapping):
    data: Dict[str, str]

    def __getitem__(self, idx: str) -> str:
        return self.data[idx].strip()

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
    
    def list_keys(self):
        return list(self.data.keys())


class BaseStucturedData(BaseFormatter):
    data: Dict[str, str] = {
        name: obj for name, obj in inspect.getmembers(st_data)
        if isinstance(obj, str) and "__" not in name
    }


class BaseExplanation(BaseFormatter):
    data: Dict[str, str] = {
        name: obj for name, obj in inspect.getmembers(explain_data)
        if isinstance(obj, str) and "__" not in name
    }


class BaseInformation(BaseFormatter):
    data: Dict[str, str] = {
        name: obj for name, obj in inspect.getmembers(info_data)
        if isinstance(obj, str) and "__" not in name
    }


class BaseExampleTable(BaseFormatter):
    data: Dict[str, str] = {
        name: obj for name, obj in inspect.getmembers(example_table)
        if isinstance(obj, dict) and "__" not in name
    }

    def __getitem__(self, idx: str) -> dict:
        return self.data[idx]


class BaseExampleText(BaseFormatter):
    data: Dict[str, str] = {
        name: obj for name, obj in inspect.getmembers(example_text)
        if isinstance(obj, str) and "__" not in name
    }


class BaseOperation(BaseFormatter):
    data: Dict[str, str] = {
        name: obj for name, obj in inspect.getmembers(operation)
        if isinstance(obj, str) and "__" not in name
    }



class Formatter(object):
    structured_data = BaseStucturedData()
    explanation = BaseExplanation()
    information = BaseInformation()
    example_table = BaseExampleTable()
    example_text = BaseExampleText()
    operation = BaseOperation()

    @classmethod
    def keys(cls, ) -> Iterable[str]:
        return [
            'structured_data',
            'explanation',
            'information',
            'example_table',
            'example_text',
            'operation'
        ]


class PropertiesOnlyFormatter(object):
    """Formatter that only includes property-related data, excluding all operations."""
    
    # Define property-only structured data
    structured_data = {
        'meta': """{
    "name": "",
    "symbol": "",  # ex) 1a
    "chemical_formula": ""
}""",
        'chemical_formula': """[
    {"value": "", "condition": ""}
]""",
        'capacity': """[
    {"value": "", "unit": "", "type": "", "condition": ""}
]""",
        'energy_density': """[
    {"value": "", "unit": "", "type": "", "condition": ""}
]""",
        'power_density': """[
    {"value": "", "unit": "", "type": "", "condition": ""}
]""",
        'voltage': """[
    {"value": "", "unit": "", "type": "", "condition": ""}
]""",
        'coulombic_efficiency': """[
    {"value": "", "unit": "", "type": "", "condition": ""}
]""",
        'cycle_life': """[
    {"value": "", "unit": "", "condition": ""}
]""",
        'electrode_thickness': """[
    {"value": "", "unit": "", "type": "", "condition": ""}
]""",
        'particle_size': """[
    {"value": "", "unit": "", "type": "", "condition": ""}
]""",
        'ionic_conductivity': """[
    {"value": "", "unit": "", "type": "", "condition": ""}
]""",
        'electronic_conductivity': """[
    {"value": "", "unit": "", "condition": ""}
]""",
        'diffusivity': """[
    {"value": "", "unit": "", "type": "", "condition": ""}
]""",
        'young_modulus': """[
    {"value": "", "unit": "", "condition": ""}
]""",
        'volume_expansion': """[
    {"value": "", "unit": "", "condition": ""}
]""",
        'activation_energy': """[
    {"value": "", "unit": "", "type": "", "condition": ""}
]""",
        'band_gap': """[
    {"value": "", "unit": "", "type": "", "condition": ""}
]""",
        'current_density': """[
    {"value": "", "unit": "", "type": "", "condition": ""}
]"""
    }
    

    # Property-only explanations 
    explanation = {
        'chemical_formula': """
chemical formula or compound of battery materials. ex) LiFePO4, LiCoO2, LiNiMnCoO2.
""",
        'capacity': """
battery capacity, typically measured in mAh/g or mAh/cm². ex) specific capacity, areal capacity, theoretical capacity.
""",
        'energy_density': """
energy density of battery materials, measured in Wh/kg or Wh/L. ex) gravimetric energy density, volumetric energy density.
""",
        'power_density': """
power density of battery materials, measured in W/kg or W/L. ex) specific power, power capability.
""",
        'voltage': """
voltage of battery cells or materials, measured in V. ex) operating voltage, discharge voltage.
""",
        'coulombic_efficiency': """
coulombic efficiency of battery materials, measured as percentage (%). ex) charge efficiency, discharge efficiency.
""",
        'cycle_life': """
number of charge-discharge cycles a battery can withstand. ex) cycle stability, cycling performance.
""",
        'electrode_thickness': """
thickness of battery electrodes, measured in μm or mm. ex) cathode thickness, anode thickness.
""",
        'particle_size': """
particle size of battery materials, measured in nm or μm. ex) particle diameter, grain size.
""",
        'ionic_conductivity': """
ionic conductivity of electrolytes or materials, measured in S/cm or mS/cm. ex) Li+ conductivity.
""",
        'electronic_conductivity': """
electronic conductivity of battery materials, measured in S/cm. ex) electrical conductivity.
""",
        'diffusivity': """
diffusion coefficient of ions in battery materials, measured in cm²/s. ex) Li+ diffusivity, diffusion constant.
""",
        'young_modulus': """
Young's modulus of battery materials, measured in GPa. ex) elastic modulus, stiffness.
""",
        'volume_expansion': """
volume expansion of battery materials during cycling, measured as percentage (%). ex) volumetric change, swelling.
""",
        'activation_energy': """
activation energy for ion transport or electrochemical reactions, measured in kJ/mol or eV. ex) ionic conductivity activation energy, electrochemical activation energy.
""",
        'band_gap': """
band gap energy of battery materials, measured in eV. ex) direct band gap, indirect band gap.
""",
        'current_density': """
current density in battery cells, measured in mA/cm² or A/g. ex) discharge current density, charging current density.
"""
    }
    
    # Property-only information  
    information = {
        'chemical_formula': """
Chemical formulas for battery materials, such as LiFePO4, LiCoO2/Gr, SiC@MnCoO2. Include all mentioned compounds.
""",
        'capacity': """
Battery capacity values, typically in mAh/g or mAh/cm². Note specific vs. areal capacity. Include conditions like temperature or C-rate if mentioned.
""",
        'energy_density': """
Energy density in Wh/kg or Wh/L. Distinguish between gravimetric and volumetric. Include measurement conditions.
""",
        'power_density': """
Power density in W/kg or W/L. Note specific or volumetric power. Include conditions like discharge rate.
""",
        'voltage': """
Voltage in V. Types include operating, discharge, or charge voltage. Include conditions like state of charge.
""",
        'coulombic_efficiency': """
Coulombic efficiency as percentage (%). Note charge or discharge efficiency. Include cycle number or conditions.
""",
        'cycle_life': """
Number of cycles before capacity fade. Often expressed as cycles to retain certain capacity percentage.
""",
        'electrode_thickness': """
Electrode thickness in μm or mm. Specify cathode or anode. Include coating or total thickness if distinguished.
""",
        'particle_size': """
Particle size in nm or μm. Types include diameter, grain size, or average size. Include distribution if mentioned.
""",
        'ionic_conductivity': """
Ionic conductivity in S/cm or mS/cm. Specify ion type (e.g., Li+, Na+). Include temperature and other conditions.
""",
        'electronic_conductivity': """
Electronic conductivity in S/cm. Note measurement method or conditions if specified.
""",
        'diffusivity': """
Diffusion coefficient in cm²/s. Specify ion type (e.g., Li+ diffusivity). Include temperature or concentration conditions.
""",
        'young_modulus': """
Young's modulus in GPa. Note measurement method or conditions like temperature.
""",
        'volume_expansion': """
Volume expansion as percentage (%). Include conditions like lithiation/delithiation or cycling.
""",
        'activation_energy': """
Activation energy in eV or kJ/mol. Note the process or reaction it refers to, e.g., diffusion or charge transfer. Include temperature range or conditions if specified.
""",
        'band_gap': """
Band gap in eV. Specify direct or indirect band gap if mentioned. Include measurement method or conditions like temperature.
""",
        'current_density': """
Current density in mA/cm² or A/cm². Types include charge, discharge, or limiting current density. Include conditions like voltage, electrolyte, or temperature.
"""
    }
    

    # Property-only examples
    example_text = {
        'chemical_formula': """
Paragraph: The LiFePO4 cathode material exhibits excellent electrochemical performance with a capacity of 170 mAh/g. LiCoO2 is another common cathode material used in lithium-ion batteries.
JSON: ```JSON
[{{"value":"LiFePO4", "condition":""}}, {{"value":"LiCoO2", "condition":""}}]
```
""",
        'capacity': """
Paragraph: The LiFePO4 cathode material delivers a high specific capacity of 170 mAh/g, while the LiCoO2 cathode achieves 150 mAh/g under standard conditions. The theoretical capacity of LiFePO4 is 178 mAh/g.
JSON: ```JSON
[{{"value":"170", "unit":"mAh/g", "type":"specific", "condition":""}}, {{"value":"150", "unit":"mAh/g", "type":"specific", "condition":""}}, {{"value":"178", "unit":"mAh/g", "type":"theoretical", "condition":""}}]
```
""",
        'energy_density': """
Paragraph: The lithium-ion battery with LiFePO4 cathode demonstrates a gravimetric energy density of 586 Wh/kg and a volumetric energy density of 1280 Wh/L.
JSON: ```JSON
[{{"value":"586", "unit":"Wh/kg", "type":"gravimetric", "condition":""}}, {{"value":"1280", "unit":"Wh/L", "type":"volumetric", "condition":""}}]
```
""",
        'power_density': """
Paragraph: The battery system achieves a specific power density of 5000 W/kg, enabling fast charging capabilities.
JSON: ```JSON
[{{"value":"5000", "unit":"W/kg", "type":"specific", "condition":""}}]
```
""",
        'voltage': """
Paragraph: The operating voltage of the LiFePO4 battery is approximately 3.4 V, while the LiCoO2 battery operates at 3.7 V.
JSON: ```JSON
[{{"value":"3.4", "unit":"V", "type":"operating", "condition":""}}, {{"value":"3.7", "unit":"V", "type":"operating", "condition":""}}]
```
""",
        'coulombic_efficiency': """
Paragraph: The battery exhibits excellent coulombic efficiency of 98% over 500 charge-discharge cycles, indicating minimal capacity loss.
JSON: ```JSON
[{{"value":"98", "unit":"%", "type":"charge", "condition":""}}]
```
""",
        'cycle_life': """
Paragraph: The Li-ion battery maintains 80% of its initial capacity after 1000 cycles, demonstrating excellent cycle stability.
JSON: ```JSON
[{{"value":"1000", "unit":"cycles", "condition":""}}]
```
""",
        'electrode_thickness': """
Paragraph: The cathode electrode has a thickness of 50 μm, while the anode electrode is 40 μm thick.
JSON: ```JSON
[{{"value":"50", "unit":"μm", "type":"cathode", "condition":""}}, {{"value":"40", "unit":"μm", "type":"anode", "condition":""}}]
```
""",
        'particle_size': """
Paragraph: The active material particles have an average diameter of 100 nm, which contributes to improved electrochemical performance.
JSON: ```JSON
[{{"value":"100", "unit":"nm", "type":"diameter", "condition":""}}]
```
""",
        'ionic_conductivity': """
Paragraph: The ionic conductivity of the solid electrolyte is 1.2 × 10^-3 S/cm at room temperature, facilitating efficient Li+ ion transport.
JSON: ```JSON
[{{"value":"1.2 × 10^-3", "unit":"S/cm", "type":"Li+", "condition":"room temperature"}}]
```
""",
        'electronic_conductivity': """
Paragraph: The electronic conductivity of the cathode material is measured at 0.5 S/cm, ensuring good electrical pathways within the electrode.
JSON: ```JSON
[{{"value":"0.5", "unit":"S/cm", "condition":""}}]
```
""",
        'diffusivity': """
Paragraph: The diffusivity of Li+ ions in the electrode material is 2.5 × 10^-10 cm²/s, which affects the rate capability of the battery.
JSON: ```JSON
[{{"value":"2.5 × 10^-10", "unit":"cm²/s", "type":"Li+", "condition":""}}]
```
""",
        'young_modulus': """
Paragraph: The Young's modulus of the electrode material is 120 GPa, indicating its mechanical stiffness and resistance to deformation.
JSON: ```JSON
[{{"value":"120", "unit":"GPa", "condition":""}}]
```
""",
        'volume_expansion': """
Paragraph: The battery electrode experiences a volume expansion of 10% during the lithiation process, which can lead to capacity fading over time.
JSON: ```JSON
[{{"value":"10", "unit":"%", "condition":"lithiation"}}]
```
""",
        'activation_energy': """
Paragraph: The activation energy for Li+ ion diffusion in the solid electrolyte is 0.5 eV, determined from Arrhenius analysis over a temperature range of 25-100°C.
JSON: ```JSON
[{{"value":"0.5", "unit":"eV", "type":"diffusion", "condition":"25-100°C"}}]
```
""",
        'band_gap': """
Paragraph: The semiconductor material exhibits a direct band gap of 1.5 eV, which is suitable for photovoltaic applications.
JSON: ```JSON
[{{"value":"1.5", "unit":"eV", "type":"direct", "condition":""}}]
```
""",
        'current_density': """
Paragraph: The electrode achieves a current density of 2 mA/cm² during the discharge process at a voltage of 3.5 V.
JSON: ```JSON
[{{"value":"2", "unit":"mA/cm²", "type":"discharge", "condition":"3.5 V"}}]
```
"""
    }
    
    # Empty operations since we're properties-only
    operation = {}

    @classmethod
    def get_property_keys(cls) -> list:
        """Return list of property keys only."""
        return list(cls.structured_data.keys())

    @classmethod
    def keys(cls) -> Iterable[str]:
        return [
            'structured_data',
            'explanation', 
            'information',
            'example_text',
            'operation'
        ]
