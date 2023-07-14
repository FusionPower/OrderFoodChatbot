# OrderFoodChatbot
Ready to order your favorite food?
This chatbot helps you make your order! Just fine-tune the model of your choice with the data in this repo, fill up the key and model_id fields in the QSR_GPT_API file and enjoy!
This project was obtained by fine-funning an OpenAI model using their API.
![image](https://github.com/FusionPower/OrderFoodChatbot/assets/54119843/4ee20eae-e59e-49ca-85db-2ddf5103eaea)

*Remember to set up your virtual environment with the requirements.txt file*
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

## Overview
The chatbot works by classifiying user requests into:
0 conversation (general)
1 greeting
2 add items to order
3 read current order
4 update an item
5 delete an item
6 do a menu lookup (is X dish vegetarian)
7 subitem configuration <- TODO
8 affirmative response
9 negative response

The performance is decent but more data could be generated to increase performance.


Instructions on how to fine-tune your model can be found here:
https://platform.openai.com/docs/guides/fine-tuning

