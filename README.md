# LEGAL-ANALYSIS

## Requirements
## Setup and Installation

1. Create an Anaconda environment:
   ```bash
   conda create -n legal-analysis python=3.9
   conda activate legal-analysis
   ```

2. Install Ollama:
   - Visit the [Ollama website](https://ollama.ai/) and download the appropriate version for your operating system.
   - Follow the installation instructions provided on the website.

3. Run Ollama with Mistral:
   ```bash
   ollama run mistral
   ```

4. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the test case:
   ```bash
   python3 testcase.py
   ```

Make sure to keep Ollama running with Mistral in a separate terminal window while executing the test case.

