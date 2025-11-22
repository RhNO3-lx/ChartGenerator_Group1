from openai import OpenAI

def get_prompt( title, 
                bg_color, 
                prompt_path = 'prompts/generate_prompt_gpt_en.md', 
                save_path = 'prompts/generated_output.md'):
    with open(prompt_path, 'r', encoding='utf-8') as file:
        generate_prompt = file.read()
    generate_prompt = generate_prompt.replace("{title}", title)
    generate_prompt = generate_prompt.replace("{color}", bg_color)

    client = OpenAI(
        api_key="sk-ug32KbbvEDPucqnaB207A5EcEd6f47Dc887c14249a12Ff43",
        base_url="https://aihubmix.com/v1"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    { 
                    "type": "text",
                    "text": generate_prompt},
                    ]
            }
        ]
    )
    #print(response.choices[0])
    generated_text = response.choices[0].message.content
    generated_text = "Generate a text image with the content of \"" + title + "\". " + generated_text
    with open(save_path, 'w', encoding='utf-8') as output_file:
        output_file.write(generated_text)
    return save_path
