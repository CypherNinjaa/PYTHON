"""Simple file existence checker."""

from pathlib import Path


def main():
	file_path = input("Enter file path: ").strip()
	path = Path(file_path)

	if path.is_file():
		print("File exists")
	else:
		print("File does not exist")


if __name__ == "__main__":
	main()