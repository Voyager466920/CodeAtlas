from backend.services.slm import analyze_file_content

sample_content = """
class MyClass:
    def my_method(self):
        pass

def my_function():
    pass
"""

result = analyze_file_content("test_file.py", sample_content)
print(result)
