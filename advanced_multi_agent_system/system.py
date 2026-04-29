
import os
import ast
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class BaseAgent:
    def __init__(self, name):
        self.name = name

    def log(self, msg):
        print(f"[{self.name}] {msg}")

class ScannerAgent(BaseAgent):
    def scan(self, repo):
        files = []
        for r, _, fs in os.walk(repo):
            for f in fs:
                if f.endswith(".py"):
                    files.append(os.path.join(r, f))
        return files

class ReviewAgent(BaseAgent):
    def analyze(self, file):
        with open(file, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and len(node.body) > 15:
                issues.append(f"Function {node.name} too long")
        if "TODO" in code:
            issues.append("Contains TODO")
        return issues, code

class GPTRefactorAgent(BaseAgent):
    def suggest(self, issues, code):
        if not OPENAI_API_KEY:
            return ["[Mock] Refactor function", "[Mock] Remove TODO"]

        prompt = f"Issues: {issues}\nImprove code:\n{code}"
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        try:
            return [response.json()["choices"][0]["message"]["content"]]
        except:
            return ["GPT failed"]

class TestAgent(BaseAgent):
    def run(self):
        return True

class GitHubPRAgent(BaseAgent):
    def create_pr(self, file, issues, suggestions):
        return f'''
AUTO PR
File: {file}

Issues:
{"".join("- "+i+"\n" for i in issues)}

Suggestions:
{"".join("- "+s+"\n" for s in suggestions)}
'''

class CodeReviewSystem:
    def __init__(self):
        self.scanner = ScannerAgent("Scanner")
        self.reviewer = ReviewAgent("Reviewer")
        self.refactor = GPTRefactorAgent("GPT")
        self.tester = TestAgent("Tester")
        self.pr = GitHubPRAgent("PR")

    def run(self, repo):
        prs = []
        files = self.scanner.scan(repo)
        for f in files:
            issues, code = self.reviewer.analyze(f)
            if not issues:
                continue
            suggestions = self.refactor.suggest(issues, code)
            if self.tester.run():
                prs.append(self.pr.create_pr(f, issues, suggestions))
        return prs
