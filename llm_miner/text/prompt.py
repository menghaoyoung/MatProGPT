PROMPT_TYPE = """First, determine whether properties exist or not. Except for chemical_formula, properties must have a numeric value. If a property does not have numeric value, do not extract it. If there is no property in the paragraph, please return an empty list.
If properties exist, you must find all the properties in paragraphs. Names of properties must be one of following:
{explanation}

You must follow below rules:
- Avoid including the same property multiple times.
- You must include only the properties, excluding the names of materials.
- If a property you find lacks a value, please exclude it.
- Chemical formulas should be extracted as strings (e.g., LiFePO4, LiCoO2/Gr, LiNi@MnCoO2).
- Battery properties typically have units like mAh/g, Wh/kg, V, %, cycles, μm, nm, S/cm, cm²/s, GPa, %.

If you are uncertain, please reply with "I do not know".

Begin!

Paragraph: The LiFePO4 cathode material exhibits a capacity of 170 mAh/g and an energy density of 586 Wh/kg. The voltage of the LiFePO4 battery is approximately 3.4 V.
List: ```JSON
["chemical_formula", "capacity", "energy_density", "voltage"]
```

Paragraph: The LiCoO2 electrode shows excellent coulombic efficiency of 98% over 500 cycles, with a cycle life exceeding 1000 cycles.
List: ```JSON
["coulombic_efficiency", "cycle_life"]
```

Paragraph: The electrode thickness is 50 μm, and the particle size of the active material is around 100 nm.
List: ```JSON
["electrode_thickness", "particle_size"]
```

Paragraph: The ionic conductivity of the electrolyte is 1.2 × 10^-3 S/cm, while the electronic conductivity of the cathode is 0.5 S/cm.
List: ```JSON
["ionic_conductivity", "electronic_conductivity"]
```

Paragraph: The diffusivity of Li+ ions in the solid electrolyte is 2.5 × 10^-10 cm²/s, and the Young's modulus of the electrode material is 120 GPa.
List: ```JSON
["diffusivity", "young_modulus"]
```

Paragraph: The battery shows a volume expansion of 10% during charging, and the power density reaches 5000 W/kg.
List: ```JSON
["volume_expansion", "power_density"]
```

Paragraph: {paragraph}
List:"""


PROMPT_EXT = """Extract the information about {prop} mentioned in the paragraph. Follow the structured data in JSON format:
{structured_data}

Strict instructions (follow exactly):
- Return JSON only. No explanatory text.
- For every numeric property, include a non-empty "unit". Use canonical units when possible (e.g., "mAh/g", "A/g", "%", "cycles", "V", "Wh/kg").
- If the paragraph shows a value as a fraction (e.g., 0.98) but the same quantity is shown as percent in the text (e.g., 98%), return the value in percent ("98") and unit "%".
- Preserve the numeric magnitude but convert to the canonical representation if necessary (see examples).
- Do NOT invent values or units not strongly implied by the paragraph.
- Each material entry must be a dictionary that includes a "meta" object with keys: "name", "symbol", "chemical_formula".

Examples (must follow these formats):
Paragraph: At a constant current density of 0.3 A/g, the first cycle capacity is about 301 mAh/g.
JSON: ```JSON
[{"meta":{"name":"","symbol":"","chemical_formula":""}, "current_density":{"value":"0.3","unit":"A/g","type":"","condition":""}, "capacity":{"value":"301","unit":"mAh/g","type":"specific","condition":"0.3 A/g"}}]
```

Paragraph: The capacity remains about 218 mAh/g after 200 cycles.
JSON: ```JSON
[{"meta":{"name":"","symbol":"","chemical_formula":""}, "capacity":{"value":"218","unit":"mAh/g","type":"specific","condition":"200 cycles"}}]
```

Paragraph: Coulombic efficiency is 0.98 and stable.
JSON: ```JSON
[{"meta":{"name":"","symbol":"","chemical_formula":""}, "coulombic_efficiency":{"value":"98","unit":"%","type":"","condition":""}}]
```

{information}

If uncertain, reply with the literal string: I do not know

Begin!

Paragraph: {paragraph}
JSON:
"""

FT_TYPE = (
    "You must decide whether properties exist or not. "
    "Except for chemical_formula, property must have a numeric value. "
    "If there is no property in the paragraph, please return an empty list. "
    "You must find all the properties in the paragraphs. "
    "Names of properties must be one of following:\n"
    "['chemical_formula', 'capacity', 'energy_density', 'power_density', 'voltage', 'coulombic_efficiency', 'cycle_life', 'electrode_thickness', 'particle_size', 'ionic_conductivity', 'electronic_conductivity', 'diffusivity', 'young_modulus', 'volume_expansion', 'activation_energy', 'band_gap', 'current_density']"
)

FT_HUMAN = "{paragraph}"
