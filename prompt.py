'''
Prompt Testing
'''

def prompt_test(series_name):
    prompt = (
        f"Analyze the price tables for the {series_name} Series. "
        "Each price in the table is determined by several parameters such as MODEL, FINISH, FUNCTION, SIZE, etc. "
        "Identify these parameter names(Available in Price table) along with their possible options and return the result in the following JSON format:\n\n"
    )

    sample_output = {
        "Parameter_1": ["Option_1", "Option_2"],
        "Parameter_2": ["Option_1", "Option_2"]
    }

    prompt += str(sample_output)

    return prompt
def prompt_index():
    prompt = (
        f"Analyze the index/toc data and return the series names with page number in below JSON format."
        "JSON Format:\n"
    )

    sample_output = [{
        "SERIES": "series_1",
        "PAGE": "page_1"
    },
    {
        "SERIES": "series_2",
        "PAGE": "page_2"
    }]

    prompt += str(sample_output)

    return prompt

def price_prompt(series,selection):
    print(selection)
    prompt=f'''
    Analze the {series} Series price table and tell me the price for the below conditions. The price will be in below JSON format.
    Conditions:
    {selection}

    Output Format:\n
    '''
    out=[{
        "price":""
    }]

    return prompt+str(out)



