import click
from query_handler import get_llm_response
from schema_validator import validate_response
from fallback_handler import get_fallback
from log_writer import log_event

@click.command()
@click.option('--query', prompt='Your query', help='The user query.')
def main(query):
    response = get_llm_response(query)
    is_valid, validated_data = validate_response(response)
    
    if is_valid:
        output = validated_data
        used_fallback = False
    else:
        output = get_fallback()
        used_fallback = True

    print(output)
    log_event(query, response, is_valid, used_fallback)

if __name__ == '__main__':
    main()
