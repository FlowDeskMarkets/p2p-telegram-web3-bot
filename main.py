from dotenv import load_dotenv
import gpt_module

def main():
    load_dotenv()
    gpt_client = gpt_module.GptClient()
    response = gpt_client.call_with_prompt("Transfer 3 eth to Benoit")
    print(response.choices[0].message.content)
    response = gpt_client.call_with_prompt("Transfer 1 usdc to Benjamin")
    print(response.choices[0].message.content)
    response = gpt_client.call_with_prompt("Transfer 15 btc to Armand")
    print(response.choices[0].message.content)
    response = gpt_client.call_with_prompt("Buy 15 btc from uniswap-v3")
    print(response.choices[0].message.content)

if __name__ == '__main__':
    main()