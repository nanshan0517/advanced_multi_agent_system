
from system import CodeReviewSystem

if __name__ == "__main__":
    system = CodeReviewSystem()
    repo_path = "./example_repo"
    prs = system.run(repo_path)

    for pr in prs:
        print("=" * 50)
        print(pr)
