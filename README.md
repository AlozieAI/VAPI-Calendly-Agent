# VAPI-Calendly-Agent

This repository contains the VAPI Agent I built using function calling and Server URL, as demonstrated in the [VAPI Server URLs & Function Calls Guide: Building a Calendly Booking Agent Video](https://youtu.be/-W9PlhA7nnY?si=mNb1Dd9WJVIG-pMd).

## Features
- **VAPI JSON Configuration:** Includes the configuration file to help you set up your own VAPI Agent.
- **VAPI Prompt:** Contains the prompt used to guide the agent's behavior.
- **Make Automation Blueprints:** Includes downloadable blueprints for automating workflows in Make (formerly Integromat).

## How to Use

### 1. Set Up Your VAPI Agent
To create your own VAPI Agent:
1. Make a POST request to `https://api.vapi.ai/assistant`.
2. Use the JSON file provided in the `VAPI-Config` folder as the request body.

### 2. Use the Make Automation Blueprints
To import and use the Make automation blueprints:
1. Download one of the automation files from the `Make-Automation-Blueprints` folder.
2. Open [Make](https://www.make.com/) and create a new scenario.
3. Click the three small dots at the bottom of the screen and select **Import Blueprint**.
4. Upload the downloaded file to get started.

### 3. Automate Calendly Booking with AI Browser Automation
To leverage the AI browser automation code for booking meetings on Calendly:
1. Copy the code from the repository or upload it to your preferred IDE (e.g., Replit).
2. Run the following command in your terminal to install the necessary dependencies:
   ```bash
   pip install -r requirements.txt

