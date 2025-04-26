{% macro get_connection_type(schema_name) %}
    {%- if target.name == 'prod' -%}
        {{ var(schema_name) }}
    {%- else -%}
        {{ var(schema_name) }}_dev
    {%- endif -%}
{% endmacro %}