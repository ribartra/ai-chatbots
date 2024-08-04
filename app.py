import requests
import time

def get_config_value(key, filename='config.json'):
    """
    Lee el archivo JSON y devuelve el valor correspondiente a la clave especificada.

    :param key: La clave cuyo valor se desea obtener.
    :param filename: El nombre del archivo JSON (por defecto 'config.json').
    :return: El valor asociado a la clave, o None si la clave no existe.
    """
    try:
        with open(filename, 'r') as file:
            config_data = json.load(file)
            return config_data.get(key, None)
    except FileNotFoundError:
        print(f"El archivo {filename} no se encontró.")
    except json.JSONDecodeError:
        print("Error al decodificar el archivo JSON.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        
TESTING=get_config_value("TESTING")
OPENAI_API_KEY = get_config_value("OPENAI_API_KEY")
OPENAI_ORG_ID = get_config_value("OPENAI_ORG_ID")
OPENAI_PROJECT_ID = get_config_value("OPENAI_PROJECT_ID")

def create_assistant():
    url = "https://api.openai.com/v1/assistants"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    data = {
        "name": "Sales Analysis Assistant",
        "description": "An assistant specialized in analyzing sales data and providing insights.",
        "model": "gpt-3.5-turbo",
        "tools":[{"type":"code_interpreter"},{"type":"file_search"}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print('Assistant created successfully:', response.json()['id'])
        return response.json()['id']
    else:
        print("Failed to create assistant:", response.text)
        return None

# Función para formatear la salida
def format_response(result):
    if not TESTING:
        # Modo normal: mostrar solo la respuesta del asistente
        return result['choices'][0]['message']['content']
    else:
        # Modo prueba: mostrar todos los detalles de manera amigable
        return f"ID: {result['id']}\nModelo: {result.get('model', 'thread_id')}\nRespuesta del asistente: {result['choices'][0]['message']['content']}\nTokens usados: {result['usage']['total_tokens']}"
    
def get_usage_log(result):
    print(f"Tokens entrada: {result['usage']['prompt_tokens']}")
    print(f"Tokens salida: {result['usage']['completion_tokens']}")
    print(f"Tokens totales usados: {result['usage']['total_tokens']}")

def chat_with_gpt(identifier, prompt, test=False):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'messages': [
            {"role": "user", "content": prompt}
        ],
        'max_tokens': 150,
        'temperature': 0.0
    }
    
    # Decide el endpoint basado en si el identificador contiene 'asst'
    if 'asst' in identifier:
        endpoint = f'https://api.openai.com/v1/assistants/{identifier}/chat'
    elif 'thread' in identifier:
        endpoint =f'https://api.openai.com/v1/threads/{identifier}/runs'
    else:
        endpoint = 'https://api.openai.com/v1/chat/completions'
        data['model'] = identifier  # Especificar el modelo solo si no es un asistente

    response = requests.post(endpoint, headers=headers, json=data)
    
    result = response.json()

    if 'error' in result:
        return result['error']['message']
    
    return format_response(result, test)

def create_thread():
    url = "https://api.openai.com/v1/threads"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print('Thread created:', response.json()['id'])
        return response.json()['id']
    else:
        print("Failed to create thread:", response.text)
        return None

def add_and_run_message(thread_id, assistant_id, message):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

    # Add a message to the thread
    message_url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    message_data = {
        "role": "user",
        "content": message
    }
    add_message_response = requests.post(message_url, headers=headers, json=message_data)
    if add_message_response.status_code != 200:
        print('Error adding message to thread:', add_message_response.text)
        return add_message_response.text  # Return or handle error appropriately

    print('Message added to thread successfully.')

    # Run the thread with the specified assistant_id
    run_url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    run_data = {
        "assistant_id": assistant_id,
        "additional_instructions": None,
        "tool_choice": None
    }
    run_response = requests.post(run_url, headers=headers, json=run_data)
    if run_response.status_code == 200:
        print('Thread run initiated successfully.')
        run_id = run_response.json()['id']
        run_response=fetch_run_result(thread_id, run_id)
    else:
        print('Error initiating thread run:', run_response.text)
        return None

    return run_response  # Return the response from running the thread


def fetch_run_result(thread_id, run_id):
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    while True:
        response = requests.get(url, headers=headers)
        run_status = response.json()
        if response.status_code != 200:
            print('Error fetching run status:', response.text)
            return None
        if run_status['status'] in ['completed', 'failed', 'cancelled']:
            break
        time.sleep(5)  # Poll every 5 seconds

    if run_status['status'] == 'completed':
        print('Run completed successfully.')
        return run_status
    else:
        print(f"Run did not complete successfully: Status is {run_status['status']}")
        return None

def fetch_messages_from_thread(thread_id):
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        messages = response.json().get('data', [])
        last_assistant_message = None
        # Loop through messages to find the last message from the assistant
        for message in messages:
            if message['role'] == 'assistant':
                last_assistant_message = message
        return last_assistant_message  # Return only the last assistant message
    else:
        print("Failed to fetch messages:", response.text)
        return None
    
def process_response(response,thread_id):
    if response is None:
        return
    if response['status'] == 'completed':
        print("Fetching messages from the thread...")
        message = fetch_messages_from_thread(thread_id)
        if message['role'] == 'assistant':
            print("Assistant:", message['content'][0]['text']['value'])  
            if TESTING:
                get_usage_log(response)

def main():

    # Ejemplo de uso
    prompt = "Hello, if I want to analyze a sales conversation, I want to understand the most critical moment, how to do this using Data Analysis, first generate samples as data and then analyze it to show it."
    model = 'gpt4'
    thread_id = None
    option='thread'

    try:
        assistant_id = create_assistant()
        if assistant_id is None:
            print('Terminating program...')
            return

        if option != 'thread':
            response = chat_with_gpt(model, prompt, test=True)
            if response != None:
                print(response) 
        else:
            thread_id = create_thread()
            if thread_id is None:
                print('Terminating program...')
                return
            while True:
                user_input = input("Usuario: ")
                if user_input.lower() == 'exit':
                    print("Ending conversation.")
                    break

                response = add_and_run_message(thread_id, assistant_id, user_input)
                process_response(response,thread_id)

    except KeyboardInterrupt:
        print("Program interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()

