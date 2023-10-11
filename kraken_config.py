import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the current working directory to the script's directory
os.chdir(script_dir)

# Set sandbox_mode to True for Sandbox/Demo, and False for Live
sandbox_mode = True

# Demo mode API key and secret
demo_apiKey = 'OZ3g7KYvKCeq2iJKGH5wybGfJWoN38nPTJWzeBWVwypyWKa48xK530CJ'
demo_secret = 'MNxwed0U45yR9+D7oQmw31kPt082vFhyLfaRlsej5uV2OgaEWCRXvnPigGhCW3xZBYwW2Fsmxm39H8IuAStQIPIB'

# Live mode API key and secret
live_apiKey = 'fksdjfksfjks94328'
live_secret = 'jksjfkjk98834'

if sandbox_mode:
    mode = 'Sandbox/Demo'
else:
    mode = 'Live'