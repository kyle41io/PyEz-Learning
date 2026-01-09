"""
AI Service for converting natural language or document text to exam JSON format.
Supports both Vietnamese and English languages using OpenAI ChatGPT.
"""
import json
import re
from typing import Dict, List, Any, Optional
from openai import OpenAI
from django.conf import settings


class ExamAIConverter:
    """
    Converts natural language descriptions or uploaded documents 
    into structured exam JSON format using OpenAI ChatGPT
    """
    
    def __init__(self):
        """Initialize the AI converter with OpenAI API"""
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in settings")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Cost-effective, fast, and capable
    
    def convert_text_to_exam(
        self, 
        text: str, 
        exam_type: str = 'multi_choice',
        language: str = 'vi'
    ) -> Dict[str, Any]:
        """
        Convert natural language text to exam JSON format.
        
        Args:
            text: Natural language description of exam questions
            exam_type: 'multi_choice' or 'coding'
            language: 'vi' for Vietnamese or 'en' for English
        
        Returns:
            Dict with 'questions' list and metadata
        """
        if exam_type == 'multi_choice':
            return self._convert_multiple_choice(text, language)
        elif exam_type == 'coding':
            return self._convert_coding_problems(text, language)
        else:
            raise ValueError(f"Invalid exam_type: {exam_type}")
    
    def validate_and_fix_json(
        self,
        json_text: str,
        exam_type: str = 'multi_choice',
        language: str = 'vi'
    ) -> Dict[str, Any]:
        """
        Validate and fix JSON format using AI.
        Handles malformed JSON, missing fields, and incorrect formats.
        
        Args:
            json_text: JSON string (possibly malformed)
            exam_type: 'multi_choice' or 'coding'
            language: 'vi' or 'en'
        
        Returns:
            Dict with corrected 'questions' list and metadata
        """
        if exam_type == 'multi_choice':
            return self._validate_fix_multiple_choice(json_text, language)
        elif exam_type == 'coding':
            return self._validate_fix_coding(json_text, language)
        else:
            raise ValueError(f"Invalid exam_type: {exam_type}")
    
    def _validate_fix_multiple_choice(self, json_text: str, language: str) -> Dict[str, Any]:
        """Validate and fix multiple choice JSON format"""
        
        prompt = f"""
You are an expert exam JSON validator and corrector. You will receive a JSON that might have errors or missing fields.

**YOUR TASK:**
1. Parse the JSON (even if malformed)
2. Fix any syntax errors
3. Ensure all required fields are present
4. Add missing fields with appropriate defaults
5. Validate data types and values
6. Return corrected JSON

**REQUIRED FORMAT FOR MULTIPLE CHOICE:**
```json
[
  {{
    "id": 1,
    "question": "Question text here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0
  }}
]
```

**VALIDATION RULES:**
1. Each question MUST have: id, question, options, correct_answer
2. options MUST be an array with at least 2 items (preferably 4)
3. correct_answer MUST be a number (index 0-3)
4. If options has only 2-3 items, add generic options to make it 4
5. If correct_answer is missing, set to 0
6. If question text is empty, use "Question {{id}}"
7. Preserve original language (Vietnamese or English)
8. Assign sequential IDs if missing (1, 2, 3...)

**INPUT JSON TO FIX:**
{json_text}

**OUTPUT:**
Return ONLY the corrected JSON array. No explanations, no markdown, no code blocks. Just the raw JSON.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert exam JSON validator. Return only valid JSON without markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={ "type": "json_object" }
            )
            json_fixed = self._extract_json(response.choices[0].message.content)
            data = json.loads(json_fixed)
            
            # Handle both wrapped object and direct array
            if isinstance(data, dict):
                questions = data.get('questions', data.get('items', []))
            else:
                questions = data
            
            # Additional validation
            validated_questions = self._validate_multiple_choice(questions)
            
            return {
                'success': True,
                'questions': validated_questions,
                'count': len(validated_questions),
                'exam_type': 'multi_choice',
                'fixed': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to validate JSON: {str(e)}",
                'questions': []
            }
    
    def _validate_fix_coding(self, json_text: str, language: str) -> Dict[str, Any]:
        """Validate and fix coding problems JSON format"""
        
        prompt = f"""
You are an expert programming exam JSON validator and corrector. You will receive a JSON that might have errors or missing fields.

**YOUR TASK:**
1. Parse the JSON (even if malformed)
2. Fix any syntax errors
3. Ensure all required fields are present
4. Add missing fields with appropriate defaults
5. Validate data types and structure
6. Return corrected JSON

**REQUIRED FORMAT FOR CODING PROBLEMS:**
```json
[
  {{
    "id": 1,
    "title": "Problem Title",
    "description": "Problem description",
    "starter_code": "def function_name():\\n    pass",
    "test_cases": [
      {{"input": "test input", "expected": "expected output"}}
    ],
    "examples": [
      {{"input": "example input", "output": "example output"}}
    ]
  }}
]
```

**VALIDATION RULES:**
1. Each problem MUST have: id, title, description, starter_code, test_cases, examples
2. If title is missing, use "Problem {{id}}"
3. If description is missing, use a generic description
4. If starter_code is missing, create: "def solution():\\n    pass"
5. If test_cases is empty, add at least one generic test case
6. If examples is empty, add at least one example
7. Preserve original language for descriptions
8. Assign sequential IDs if missing (1, 2, 3...)

**INPUT JSON TO FIX:**
{json_text}

**OUTPUT:**
Return ONLY the corrected JSON array. No explanations, no markdown, no code blocks. Just the raw JSON.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert programming exam JSON validator. Return only valid JSON without markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={ "type": "json_object" }
            )
            json_fixed = self._extract_json(response.choices[0].message.content)
            data = json.loads(json_fixed)
            
            # Handle both wrapped object and direct array
            if isinstance(data, dict):
                problems = data.get('questions', data.get('problems', data.get('items', [])))
            else:
                problems = data
            
            # Additional validation
            validated_problems = self._validate_coding_problems(problems)
            
            return {
                'success': True,
                'questions': validated_problems,
                'count': len(validated_problems),
                'exam_type': 'coding',
                'fixed': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to validate JSON: {str(e)}",
                'questions': []
            }
    
    def _convert_multiple_choice(self, text: str, language: str) -> Dict[str, Any]:
        """Convert text to multiple choice questions JSON"""
        
        prompt = f"""
You are an expert exam creator. Convert the following text into a structured JSON format for multiple choice questions.

The text may be in Vietnamese or English. Please analyze it carefully and extract all questions.

**REQUIRED JSON FORMAT:**
```json
[
  {{
    "id": 1,
    "question": "Question text here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0
  }}
]
```

**IMPORTANT RULES:**
1. Each question MUST have exactly 4 options (A, B, C, D)
2. correct_answer is the index (0-3) of the correct option
3. Preserve the original language of questions (Vietnamese or English)
4. Extract ALL questions from the text
5. Assign sequential IDs starting from 1
6. If options are labeled (A, B, C, D), remove the labels and just keep the text
7. If correct answer is indicated (e.g., "Đáp án: B"), convert it to index (B = 1)

**TEXT TO CONVERT:**
{text}

**OUTPUT:**
Return ONLY the JSON array, no explanation, no markdown formatting, no code blocks. Just the raw JSON.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert exam creator. Convert text to multiple choice questions in JSON format without markdown."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={ "type": "json_object" }
            )
            json_text = self._extract_json(response.choices[0].message.content)
            data = json.loads(json_text)
            
            # Handle both wrapped object and direct array
            if isinstance(data, dict):
                questions = data.get('questions', data.get('items', []))
            else:
                questions = data
            
            # Validate and clean the questions
            validated_questions = self._validate_multiple_choice(questions)
            
            return {
                'success': True,
                'questions': validated_questions,
                'count': len(validated_questions),
                'exam_type': 'multi_choice'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'questions': []
            }
    
    def _convert_coding_problems(self, text: str, language: str) -> Dict[str, Any]:
        """Convert text to coding problems JSON"""
        
        prompt = f"""
You are an expert programming exam creator. Convert the following text into a structured JSON format for coding problems.

The text may be in Vietnamese or English. Please analyze it carefully and extract all coding problems.

**REQUIRED JSON FORMAT:**
```json
[
  {{
    "id": 1,
    "title": "Problem Title",
    "description": "Detailed problem description with requirements",
    "starter_code": "def function_name():\\n    # Your code here\\n    pass",
    "test_cases": [
      {{"input": "test input", "expected": "expected output"}},
      {{"input": "test input 2", "expected": "expected output 2"}}
    ],
    "examples": [
      {{"input": "example input", "output": "example output"}}
    ]
  }}
]
```

**IMPORTANT RULES:**
1. Each problem needs a clear title and description
2. Provide starter_code with function signature (Python)
3. Include at least 2-3 test_cases for validation
4. Add 1-2 examples to help students understand
5. Preserve the original language for descriptions
6. Extract ALL problems from the text
7. Assign sequential IDs starting from 1

**TEXT TO CONVERT:**
{text}

**OUTPUT:**
Return ONLY the JSON array, no explanation, no markdown formatting, no code blocks. Just the raw JSON.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert programming exam creator. Convert text to coding problems in JSON format without markdown."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={ "type": "json_object" }
            )
            json_text = self._extract_json(response.choices[0].message.content)
            data = json.loads(json_text)
            
            # Handle both wrapped object and direct array
            if isinstance(data, dict):
                problems = data.get('questions', data.get('problems', data.get('items', [])))
            else:
                problems = data
            
            # Validate and clean the problems
            validated_problems = self._validate_coding_problems(problems)
            
            return {
                'success': True,
                'questions': validated_problems,
                'count': len(validated_problems),
                'exam_type': 'coding'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'questions': []
            }
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from AI response, removing markdown formatting"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find JSON array or object
        json_match = re.search(r'\[[\s\S]*\]|\{[\s\S]*\}', text)
        if json_match:
            return json_match.group(0)
        
        return text.strip()
    
    def _validate_multiple_choice(self, questions: List[Dict]) -> List[Dict]:
        """Validate and clean multiple choice questions"""
        validated = []
        
        for i, q in enumerate(questions):
            try:
                # Ensure required fields
                question = {
                    'id': q.get('id', i + 1),
                    'question': str(q.get('question', '')),
                    'options': q.get('options', []),
                    'correct_answer': int(q.get('correct_answer', 0))
                }
                
                # Validate options
                if len(question['options']) < 2:
                    continue  # Skip invalid questions
                
                # Ensure correct_answer is within range
                if question['correct_answer'] >= len(question['options']):
                    question['correct_answer'] = 0
                
                validated.append(question)
            except (ValueError, TypeError, KeyError):
                continue  # Skip invalid questions
        
        return validated
    
    def _validate_coding_problems(self, problems: List[Dict]) -> List[Dict]:
        """Validate and clean coding problems"""
        validated = []
        
        for i, p in enumerate(problems):
            try:
                # Ensure required fields
                problem = {
                    'id': p.get('id', i + 1),
                    'title': str(p.get('title', f'Problem {i + 1}')),
                    'description': str(p.get('description', '')),
                    'starter_code': str(p.get('starter_code', 'def solution():\n    pass')),
                    'test_cases': p.get('test_cases', []),
                    'examples': p.get('examples', [])
                }
                
                # Validate test cases
                if not problem['test_cases']:
                    problem['test_cases'] = [{'input': '', 'expected': ''}]
                
                validated.append(problem)
            except (ValueError, TypeError, KeyError):
                continue  # Skip invalid problems
        
        return validated
    
    def extract_text_from_file(self, file_path: str) -> Optional[str]:
        """
        Extract text from uploaded file (txt, pdf, docx, etc.)
        
        Args:
            file_path: Path to the uploaded file
        
        Returns:
            Extracted text content or None if failed
        """
        import os
        from pathlib import Path
        
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_ext == '.pdf':
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            
            elif file_ext in ['.doc', '.docx']:
                # For Word documents, we'd need python-docx
                # For now, return an error message
                return None
            
            else:
                # Unsupported format
                return None
                
        except Exception as e:
            print(f"Error extracting text from file: {e}")
            return None
    
    def convert_file_to_exam(
        self, 
        file_path: str, 
        exam_type: str = 'multi_choice',
        language: str = 'vi'
    ) -> Dict[str, Any]:
        """
        Convert uploaded file to exam JSON format.
        
        Args:
            file_path: Path to uploaded file
            exam_type: 'multi_choice' or 'coding'
            language: 'vi' or 'en'
        
        Returns:
            Dict with 'questions' list and metadata
        """
        # Extract text from file
        text = self.extract_text_from_file(file_path)
        
        if text is None:
            return {
                'success': False,
                'error': 'Could not extract text from file. Please use .txt or .pdf format.',
                'questions': []
            }
        
        if not text.strip():
            return {
                'success': False,
                'error': 'File is empty or contains no readable text.',
                'questions': []
            }
        
        # Convert extracted text to exam format
        return self.convert_text_to_exam(text, exam_type, language)


# Singleton instance
_converter_instance = None

def get_ai_converter() -> ExamAIConverter:
    """Get or create singleton AI converter instance"""
    global _converter_instance
    if _converter_instance is None:
        _converter_instance = ExamAIConverter()
    return _converter_instance
