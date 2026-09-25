SET( GENERATED_SRCS
{%- for headerFile in headerFiles %}
	{{ headerFile }}.hpp
{%- endfor %}
{%- for sourceFile in sourceFiles %}
	{{ sourceFile }}.cpp
{%- endfor %}
)
