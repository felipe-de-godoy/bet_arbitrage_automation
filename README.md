## Bet Arbitrage Automation

This Git repository contains a collection of functions and scripts for automating the process of finding and placing value bets in the betting market. The goal is to identify underpriced bets and send notifications to users to take advantage of these opportunities.

### Repository Structure

The repository is organized into the following structure:

![Arquitetura_AWS_MagicBet](https://github.com/felipe-de-godoy/bet_arbitrage_automation/assets/48608521/94b2dbab-9258-417a-a141-bd8608297ff8)

### Installation

To install and deploy the code on AWS Lambda, follow these steps:

1. Initialize a new directory.
2. Open a terminal and navigate to the directory.
3. Run the following commands to install the required Python packages:

```bash
pip3 install --target ./package pandas==1.2.4 --upgrade
pip3 install --target ./package numpy==1.19.5 --upgrade
pip3 install --target ./package s3fs==2021.08.0 --upgrade
pip3 install --target ./package requests==2.25.1 --upgrade
pip3 install --target ./package pyTelegramBotAPI --upgrade
```

## Deployment Instructions

To deploy the code on AWS Lambda, follow these steps:

1. Change directory to `package`:
```bash
cd package
```

Zip the contents:

```bash
zip -r ../Pacote_Magic_Bet_Lambda_V0.zip .
```

Return to the root directory:

```bash
cd ..
```

Add the lambda_funcao.py file to the existing zip file:

```bash
zip -g Pacote_Magic_Bet_Lambda_V0.zip lambda_funcao.py
```
Upload to the lambda in your account

Package History
The deployment package Pacote_Magic_Bet_Lambda_V0.zip can now be uploaded to AWS Lambda. Please refer to the AWS Lambda documentation for detailed instructions on deploying a Python package.

About
This project is developed for bet arbitrage automation. For any questions or inquiries, please contact the project maintainer.
