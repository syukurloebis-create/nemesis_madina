# CP2 Acceptance Matrix

## Parser
| Requirement | Test | Status |
|-------------|------|--------|
| Parse empty file | test_parse_empty | ⏳ |
| Parse syntax valid | test_parse_syntax_valid | ⏳ |
| Parse syntax error | test_parse_syntax_error | ⏳ |
| Parse UTF-8 | test_parse_utf8 | ⏳ |
| Parse multiline string | test_parse_multiline_string | ⏳ |
| Parse async | test_parse_async | ⏳ |
| Parse match-case | test_parse_match_case | ⏳ |
| Parse walrus | test_parse_walrus | ⏳ |
| Parse decorators | test_parse_decorators | ⏳ |
| Parse type annotations | test_parse_type_annotations | ⏳ |

## Visitor
| Requirement | Test | Status |
|-------------|------|--------|
| Visit module | test_visit_module | ⏳ |
| Visit class | test_visit_class | ⏳ |
| Visit function | test_visit_function | ⏳ |
| Visit async function | test_visit_async_function | ⏳ |
| Visit assignment | test_visit_assignment | ⏳ |
| Visit import | test_visit_import | ⏳ |
| Visit import from | test_visit_import_from | ⏳ |
| Visit if | test_visit_if | ⏳ |
| Visit while | test_visit_while | ⏳ |
| Visit for | test_visit_for | ⏳ |
| Visit try | test_visit_try | ⏳ |
| Visit lambda | test_visit_lambda | ⏳ |

## Normalizer
| Requirement | Test | Status |
|-------------|------|--------|
| Canonical ordering | test_normalize_order | ⏳ |
| String normalization | test_normalize_string | ⏳ |
| Empty collections | test_normalize_empty | ⏳ |
| Deterministic | test_normalize_deterministic | ⏳ |

## Serializer
| Requirement | Test | Status |
|-------------|------|--------|
| Canonical JSON | test_serialize_canonical | ⏳ |
| Deterministic | test_serialize_deterministic | ⏳ |
| Roundtrip | test_serialize_roundtrip | ⏳ |