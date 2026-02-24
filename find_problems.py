import os

def find_problems(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.md', '.txt', '.env')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if 'problem' in line.lower() and ('1' in line or '2' in line or '3' in line or '4' in line or '5' in line or '6' in line or '7' in line or '8' in line):
                                print(f"Found in {path} line {i+1}: {line.strip()}")
                except:
                    pass

if __name__ == "__main__":
    find_problems(".")
