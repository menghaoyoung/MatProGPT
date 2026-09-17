PROMPT_CATEGORIZE = """Decide if the paragraph is about battery science/technology or not.

Rules:
- Return ["battery"] only when the paragraph is related to batteries or electrochemical energy storage. Indicators include terms like battery, cathode/anode, electrolyte, separator, solid-state, LIB/NIB/SIB, SEI, capacity (mAh/g), current density, voltage, cycle life, coin cell, pouch cell, half-cell/full cell, rate capability, Coulombic efficiency, impedance.
- Return ["non battery"] when the paragraph does not concern batteries or electrochemical cells.
- Output must be exactly one of ["battery"] or ["non battery"]. No extra text.

Begin!

Paragraph: A LiFePO4 cathode delivers an initial discharge capacity of 155 mAh g^-1 at 0.1 C and retains 92% capacity after 200 cycles at 25 °C in a coin cell using a 1 M LiPF6 EC/DEC electrolyte.
List: ["battery"]

Paragraph: Metal-organic frameworks (MOFs) show high surface areas and tunable pore structures enabling gas storage and separation applications without discussing electrochemical testing or cells.
List: ["non battery"]

Paragraph: {paragraph}
List:
"""


FT_CATEGORIZE = (
    "Classify the paragraph as battery-related or not. "
    "Output exactly one label: [\"battery\"] or [\"non battery\"]. "
    "Consider terms such as cathode, anode, electrolyte, SEI, capacity (mAh/g), cycle life, voltage, coin/pouch cell as evidence of battery content."
)

FT_HUMAN = "{paragraph}"