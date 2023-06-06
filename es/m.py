import re

string = "João 6:35Anton era fascina"

# Add a space between a number and a letter
result = re.sub(r"(\d)([A-Za-z])", r"\1 \2", string)

print(result)
