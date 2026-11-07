import streamlit as st
import pandas as pd
import itertools
import re

st.set_page_config(page_title="Generador de Tablas de Verdad", page_icon="🧠")

st.title("🧠 Generador de Tablas de Verdad")
st.write("Ingresa una expresión lógica para generar su tabla de verdad.")

st.markdown("""
**Operadores disponibles:**
- ∧ AND (Y)
- ∨ OR (O)
- ¬ NOT (Negación)
- ⊕ XOR (O exclusivo)
- → Implicación
- ↔ Bicondicional
""")

expression = st.text_input(
    "Expresión lógica:",
    placeholder="Ejemplo: (A ∧ B) → ¬C"
)

def tokenize(expr):
    expr = expr.replace(" ", "")
    tokens = re.findall(r"<->|->|[A-Za-z][A-Za-z0-9]*|[()¬∧∨⊕↔]", expr)
    if "".join(tokens) != expr:
        raise ValueError("La expresión contiene caracteres no válidos.")

    aliases = {
        "&": "∧", "|": "∨", "!": "¬",
        "AND": "∧", "OR": "∨", "NOT": "¬",
        "XOR": "⊕", "->": "→", "<->": "↔"
    }
    return [aliases.get(t, t) for t in tokens]

def evaluate(expr, values):
    tokens = tokenize(expr)
    position = 0

    def match(*ops):
        nonlocal position
        if position < len(tokens) and tokens[position] in ops:
            op = tokens[position]
            position += 1
            return op
        return None

    def primary():
        nonlocal position
        if match("("):
            result = equivalence()
            if not match(")"):
                raise ValueError("Falta un paréntesis de cierre.")
            return result

        if position >= len(tokens):
            raise ValueError("Expresión incompleta.")

        variable = tokens[position]
        position += 1

        if variable not in values:
            raise ValueError(f"Variable desconocida: {variable}")
        return values[variable]

    def negation():
        if match("¬"):
            return not negation()
        return primary()

    def conjunction():
        result = negation()
        while match("∧"):
            right = negation()
            result = result and right
        return result

    def exclusive():
        result = conjunction()
        while match("⊕"):
            right = conjunction()
            result = result != right
        return result

    def disjunction():
        result = exclusive()
        while match("∨"):
            right = exclusive()
            result = result or right
        return result

    def implication():
        result = disjunction()
        if match("→"):
            right = implication()
            return (not result) or right
        return result

    def equivalence():
        result = implication()
        while match("↔"):
            right = implication()
            result = result == right
        return result

    result = equivalence()

    if position != len(tokens):
        raise ValueError("La expresión contiene operadores o símbolos incorrectos.")

    return result

if st.button("Generar tabla de verdad"):
    try:
        tokens = tokenize(expression)
        variables = sorted(set(
            t for t in tokens
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", t)
            and t not in ("AND", "OR", "NOT", "XOR")
        ))

        if not variables:
            st.error("Ingresa al menos una variable lógica.")
        else:
            rows = []

            for combination in itertools.product([True, False], repeat=len(variables)):
                values = dict(zip(variables, combination))
                result = evaluate(expression, values)

                rows.append({
                    **{v: "V" if values[v] else "F" for v in variables},
                    "Resultado": "V" if result else "F"
                })

            st.success("¡Tabla de verdad generada correctamente!")
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

    except Exception as error:
        st.error(f"Error: {error}")
