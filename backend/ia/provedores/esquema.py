"""Utilitários compartilhados para schemas de saída estruturada."""


def schema_estrito(schema):
    """Remove valores padrão e exige propriedades em objetos JSON."""
    if isinstance(schema, list):
        return [schema_estrito(item) for item in schema]
    if not isinstance(schema, dict):
        return schema
    resultado = {chave: schema_estrito(valor) for chave, valor in schema.items() if chave != "default"}
    if resultado.get("type") == "object":
        resultado["additionalProperties"] = False
        resultado["required"] = list(resultado.get("properties", {}))
    return resultado
